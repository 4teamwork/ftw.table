from zope.interface import Interface
from zope import schema


class ITableGenerator(Interface):
    """generates html tables.
    """


class ITableSource(Interface):
    """Multi-Adapter interface for table source providers (named adapter).

    Discriminators:
    - `config`: Table source configuration (providing `ITableSourceConfig`)
    - `request`: Request object (for easy customization using Browserlayers)


    """

    def __init__(config, request):
        """Initialize adapter.
        """

    def build_query():
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """

    def validate_base_query(query):
        """Validates and fixes the base query. Returns the query object.
        """

    def extend_query_with_ordering(query):
        """Extends the given `query` with ordering information and returns
        the new query.
        """

    def extend_query_with_textfilter(query):
        """Extends the given `query` with text filters. This is only done when
        config's `filter_text` is set.
        """

    def extend_query_with_batching(query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        When `lazy` is set to `False` in the configuration, this method is
        not called.
        """

    def search_results(query):
        """Executes the query and returns a tuple of `results` and `length`.
        """

    def group_results(results, column):
        """Does the grouping of the `results` by a specific `column` (dict
        based column definition used by generator utility). It modifies the
        results by extending each row with a group information. For keeping
        the row untouched, replaces each row with a tuple containing group
        and row, the generator utility will unpack the tuple and work with
        the row again.
        """


class ITableSourceConfig(Interface):
    """A table source config provides information for the table source such as
    a base query, filtering information etc.
    Usually the table source config is the view itselve (e.g. a table in
    tabbedview).
    """

    sort_on = schema.TextLine(
        title=u'Sort by attribute / key',
        description=u'Name of attribute or key on a item to sort with.')

    sort_reverse = schema.Bool(
        title=u'Reverse ordering',
        description=u'If `True` the order of the elements is reversed '
        'after sorting.',
        default=False)

    filter_text = schema.TextLine(
        title=u'Filter the elements by text',
        description=u'Text which is used for filtering the elements. '
        'Dependening on the source there may also be a index defined.')

    batching_enabled = schema.Bool(
        title=u'Batching is enabled',
        description=u'`True` if batching is enabled. This is used for '
        'generating lazy sets of results.')

    batching_pagesize = schema.Int(
        title=u'Maximum elements on one page.',
        description=u'Number of elements displayed on one page when '
        'batching is enabled.')

    batching_current_page = schema.Int(
        title=u'Current page number',
        description=u'The page number the user is currently on, used when '
        'batching is enabled. The first page is number 1.',
        default=1)

    lazy = schema.Bool(
        title=u'Make a lazy query',
        description=u'A lazy query only laods the current page but pretend to '
        'to have all records. This normally good for performance, but in some '
        'cases such as "select-all" feature we should respect batching and '
        'should not be lazy.',
        default=True)

    def update_config():
        """Is called before get_base_query() is called. This method is used
        for dynamically configuring / updating the attributes of the config
        object.
        """

    def get_base_query():
        """Returns the base query for a specific table source type
        (e.g. portal_catalog, sqlalchemy, dict, ...).
        """


class ICatalogTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations used by the
    portal_catalog table source.
    See: catalog_source.py
    """

    filter_path = schema.TextLine(
        title=u'Path filter',
        description=u'Only show objects within this path. If the path is None '
        'no path filter will be applied (all objects are shown). See also '
        'the `depth` attribute.',
        default=None)

    depth = schema.Int(
        title=u'Recursivity depth',
        description=u'Defines the recursivity depth, how depth the contents '
        'should be searched. If it set to -1 (default) the recursivity is '
        'infinite, that means all direct or indirect children are found. If '
        'set to 1 it will only find direct children. If set to 0 it will only '
        'find the current context if it matches the other criterias.',
        default=-1)

    types = schema.List(
        title=u'Portal types filter',
        description=u'Filter results by portal type.',
        value_type=schema.TextLine(),
        default=[])

    object_provides = schema.TextLine(
        title=u'Object provides interface dotted name',
        description=u'Interface name which the objects have to provide.')

    search_options = schema.Dict(
        title=u'Additional search options',
        description=u'Additional options for filtering results.',
        key_type=schema.TextLine(),
        value_type=schema.Field(),
        default={})

    custom_sort_indexes = schema.Dict(
        title=u'Custom sort indexes',
        description=u'Provides custom sort mechanisms for certain '
        'index types.',
        key_type=schema.TextLine(
            title=u'portal_catalog index type',
            description=u'Name of a portal_catalog index type '
            '(e.g. Products.PluginIndexes.DateIndex.DateIndex)'),
        value_type=schema.Field(
            title=u'custom sort method',
            description=u'pointer to a custom sort method (e.g. '
            'lambda results, sort_on, reverse: ...)'))

    search_index = schema.TextLine(
        title=u'Search index',
        description=u'Search the `filter_text` in this index.',
        default=u'SearchableText')
