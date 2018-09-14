from copy import deepcopy
from ftw.table.basesource import BaseTableSource
from ftw.table.basesource import BaseTableSourceConfig
from ftw.table.interfaces import ICatalogTableSourceConfig
from ftw.table.interfaces import ITableSource
from itertools import takewhile
from Products.CMFPlone.utils import getToolByName
from Products.ZCatalog.Lazy import LazyValues  # This will move in ZCatalog 4!
from Products.ZCTextIndex.ParseTree import ParseError
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


try:
    from zope.component.hooks import getSite
except ImportError:
    # plone 4.0 support
    from zope.app.component.hooks import getSite


# The here whitelisted catalog indexes are taken from the request
# and merged into the catalog query.
ALLOWED_CATALOG_QUERY_INDEXES = {
    'labels': lambda value: map(str.strip, value.split(',')),
    }


def default_custom_sort(results, sort_on, reverse):
    """Default custom sort method wich gets value to sort for by getting
    the attribute `sort_on` from the record.
    """

    def datetime_compare(x, y):
        a = getattr(x, sort_on, None)
        b = getattr(y, sort_on, None)
        if a is None and b is None:
            return 0
        elif a is None:
            return -1
        elif b is None:
            return 1
        # we are not able to compare datetime and date objects. So
        # let's just use strings.
        return cmp(str(a), str(b))

    return sorted(results,
                  cmp=datetime_compare,
                  reverse=reverse)


def remove_rid_from_brains(rid, brains):
    if rid not in brains._seq:
        return

    # Remove rid from sequence
    if isinstance(brains._seq, LazyValues):
        # ._seq is a LazyValues instance with a ._seq of 3-tuples, the middle
        # one of which is the rid
        #
        # The `rid in brains._seq` early abort still works so we do not end up
        # emulating [-1] on a miss
        position = sum(1 for lazyvalue in takewhile(lambda lazyvalue: rid not in lazyvalue, brains._seq._seq))
        brains._seq._seq.pop(position)
    elif isinstance(brains._seq, list):
        # ._seq is a list
        position = brains._seq.index(rid)
        brains._seq.pop(position)
    else:
        # We've encountered something we do not know of, abort
        return

    # Drop cache when it exists
    brains._data.pop(position, None)

    # Restore correct counts
    brains._len -= 1
    brains.actual_result_count -= 1


class DefaultCatalogTableSourceConfig(BaseTableSourceConfig):
    """Mixin / base class for a catalog table source config.
    """

    implements(ICatalogTableSourceConfig)

    depth = -1
    types = []
    object_provides = None
    batching_enabled = True
    search_options = {}
    custom_sort_indexes = {
            'Products.PluginIndexes.DateIndex.DateIndex': default_custom_sort}
    search_index = 'SearchableText'

    def get_base_query(self):
        """Returns the base query for a specific table source type
        (e.g. portal_catalog, sqlalchemy, dict, ...).
        """

        # get default query
        query = deepcopy(self.search_options)

        for key, value in query.items():
            if callable(value):
                query[key] = value(self.context)

        if not query:
            query = {}

        # extend with path filter, if configured
        if 'path' not in query and getattr(self, 'filter_path', None):
            query['path'] = {'query': self.filter_path,
                             'depth': self.depth}

        # extend with types
        if 'types' not in query and self.types:
            query['portal_type'] = self.types

        # filter object_provides
        if 'object_provides' not in query and self.object_provides:
            query['object_provides'] = self.object_provides

        query = self.update_query_with_request_values(query)
        return query

    def update_query_with_request_values(self, query):
        for index_name, normalizer in ALLOWED_CATALOG_QUERY_INDEXES.items():
            value = self.request.form.get(index_name, None)
            if not value:
                continue

            if callable(normalizer):
                value = normalizer(value)

            if value:
                query[index_name] = value

        return query


class CatalogTableSource(BaseTableSource):
    """Table source adapter implementing portal_catalog search for plone.
    """

    implements(ITableSource)
    adapts(ICatalogTableSourceConfig, Interface)

    def __init__(self, config, request):
        super(CatalogTableSource, self).__init__(config, request)
        self._catalog = None

    @property
    def catalog(self):
        if self._catalog is None:
            self._catalog = getToolByName(getSite(), 'portal_catalog')
        return self._catalog

    def validate_base_query(self, query):
        """Validates and fixes the base query. Returns the query object.
        It may raise e.g. a `ValueError` when something's wrong.
        """

        if not isinstance(query, dict):
            raise ValueError('Expected a dict from get_base_query() of ' + \
                                 str(self.config))

        return query

    def extend_query_with_ordering(self, query):
        """Extends the given `query` with ordering information and returns
        the new query.
        """

        # special handling for EXTJ grid reordering
        if self.request.get('sort', '') == 'draggable':
            query['sort_on'] = 'getObjPositionInParent'
            if self.config.sort_reverse:
                query['sort_order'] = 'reverse'

        # ordering
        if 'sort_on' not in query and self.config.sort_on:
            query['sort_on'] = self.config.sort_on
            if self.config.sort_reverse:
                query['sort_order'] = 'reverse'

        # handle custom sort indexes
        if 'sort_on' in query:
            index = self.catalog._catalog.indexes.get(
                self.config.sort_on, None)

            if index is not None:
                index_type = index.__module__
                if index_type in self.config.custom_sort_indexes:
                    del query['sort_on']
                    if 'sort_order' in query:
                        del query['sort_order']
                    self.config._custom_sort_method = \
                        self.config.custom_sort_indexes.get(index_type)

        # special handling for EXTJ grid reordering
        if query.get('sort_on') == 'draggable':
            query['sort_on'] = 'getObjPositionInParent'

        return query

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

        if len(text):
            if not text.endswith('*'):
                text += '*'
            query[self.config.search_index] = text

        return query

    def extend_query_with_batching(self, query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        """

        # Catalog results are lazy - let the plone `Batch` handle this..
        return query

    def search_results(self, query):
        """Executes the query and returns a tuple of `results`.

        Optionally exclude the exact object match from path queries.
        """
        try:
            brains = self.catalog(**query)
            if getattr(self.config, 'include_searchroot', False):
                return brains
            querypath = query.get('path')
            searchroot = None
            if isinstance(querypath, str):
                searchroot = querypath
            elif isinstance(querypath, dict):
                searchroot = querypath.get('query')
            if searchroot:
                rid = self.catalog.getrid(searchroot)
                remove_rid_from_brains(rid, brains)
            return brains
        except ParseError:
            return tuple()
