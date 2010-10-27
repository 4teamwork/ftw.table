from Products.CMFPlone.utils import getToolByName
from ftw.table.basesource import BaseTableSourceConfig, BaseTableSource
from ftw.table.interfaces import ITableSource, ICatalogTableSourceConfig
from zope.app.component.hooks import getSite
from zope.component import adapts
from zope.interface import implements, Interface


def default_custom_sort(results, order_by, reverse):
    """Default custom sort method wich gets value to sort for by getting
    the attribute `order_by` from the record.
    """

    return sorted(results,
                  cmp=lambda aa, bb: cmp(getattr(aa, order_by),
                                         getattr(bb, order_by)),
                  reverse=reverse)


class DefaultCatalogTableSourceConfig(BaseTableSourceConfig):
    """Mixin / base class for a catalog table source config.
    """

    implements(ICatalogTableSourceConfig)

    filter_path = None
    depth = -1
    types = []
    search_options = {}
    custom_sort_indexes = {
            'Products.PluginIndexes.DateIndex.DateIndex': default_custom_sort}
    filter_index = 'SearchableText'

    def get_base_query(self):
        """Returns the base query for a specific table source type
        (e.g. portal_catalog, sqlalchemy, dict, ...).
        """

        # get default query
        query = self.search_options

        # extend with path filter, if configured
        if 'path' not in query and self.filter_path:
            query['path'] = {'query': self.filter_path,
                             'depth': self.depth}

        # extend with types
        if 'types' not in query and self.types:
            query['portal_type'] = self.types

        # filter object_provides
        if 'object_provides' not in query and self.object_provides:
            query['object_provides'] = self.object_provides

        return self.search_options


class CatalogTableSource(BaseTableSource):
    """Table source adapter implementing portal_catalog search for plone.
    """

    implements(ITableSource)
    adapts(ICatalogTableSourceConfig, Interface)

    @property
    def catalog(self):
        try:
            return self._catalog
        except AttributeError:
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

    def extend_query_with_ording(self, query):
        """Extends the given `query` with ordering information and returns
        the new query.
        """

        # ordering
        if 'sort_on' not in query and self.config.order_by:
            query['sort_on'] = self.config.order_by
            if self.config.order_reverse:
                query['sort_order'] = 'reverse'

        # handle custom sort indexes
        if 'sort_on' in query:
            index = self.catalog._catalog.indexes.get(
                self.config.order_by, None)
            if index is not None:
                index_type = index.__module__
                if index_type in self.custom_sort_indexes:
                    del query['sort_on']
                    if 'sort_order' in query:
                        del query['sort_order']
                    self._custom_sort_method = \
                        self.custom_sort_indexes.get(index_type)

        return query

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

        if len(text):
            if not text.endswith('*'):
                text += '*'
            query[self.config.filter_index] = text

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
        """

        results = self.catalog(**query)

        if getattr(self, '_custom_sort_method', None) is not None:
            results = self._custom_sort_method(results,
                                               self.config.order_by,
                                               self.config.order_reverse)

        return results
