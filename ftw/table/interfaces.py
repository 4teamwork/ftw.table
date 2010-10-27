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


class ITableSourceConfig(Interface):
    """A table source config provides information for the table source such as
    a base query, filtering information etc.
    Usually the table source config is the view itselve (e.g. a table in
    tabbedview).
    """

    order_by = schema.TextLine(
        title=u'Order by keyword',
        description=u'Name of attribute or key on a item to sort with.')

    order_reverse = schema.Bool(
        title=u'Reverse ordering',
        description=u'If `True` the order of the elements is reversed '
        'after sorting.')

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
        'batching is enabled. The first page is number 1.')

    def get_base_query():
        """Returns the base query for a specific table source type
        (e.g. portal_catalog, sqlalchemy, dict, ...).
        """
