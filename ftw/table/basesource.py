from ftw.table.interfaces import ITableSourceConfig, ITableSource
from zope.component import adapts
from zope.interface import implements, Interface


class BaseTableSourceConfig(object):
    """Base implementation of a table source configuration.
    """

    implements(ITableSourceConfig)

    sort_on = 'sortable_title'
    sort_reverse = False
    filter_text = ''
    batching_enabled = False
    batching_pagesize = None
    batching_current_page = 1
    lazy = True

    def update_config(self):
        """Is called before get_base_query() is called. This method is used
        for dynamically configuring / updating the attributes of the config
        object.
        """

        pass

    def get_base_query(self):
        """Returns the base query for a specific table source type
        (e.g. portal_catalog, sqlalchemy, dict, ...).
        """

        raise NotImplemented


class BaseTableSource(object):
    """Base adapter for `ITableSource` adapters.
    """

    implements(ITableSource)
    adapts(ITableSourceConfig, Interface)

    def __init__(self, config, request):
        """Initialize adapter.
        """

        self.config = config
        self.request = request

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """

        # initalize config
        self.config.update_config()

        # get the base query from the config
        query = self.config.get_base_query()
        query = self.validate_base_query(query)

        # ordering
        query = self.extend_query_with_ording(query)

        # filter
        if self.config.filter_text:
            query = self.extend_query_with_textfilter(
                query, self.config.filter_text)

        # batching
        if self.config.batching_enabled and not self.lazy:
            query = self.extend_query_with_batching(query)

        return query

    def validate_base_query(self, query):
        """Validates and fixes the base query. Returns the query object.
        It may raise e.g. a `ValueError` when something's wrong.
        """

        return query

    def extend_query_with_ording(self, query):
        """Extends the given `query` with ordering information and returns
        the new query.
        """

        return query

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

        return query

    def extend_query_with_batching(self, query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        """

        return query

    def search_results(self, query):
        """Executes the query and returns a tuple of `results`.
        """

        raise NotImplemented
