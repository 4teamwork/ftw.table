from zope import schema, interface

class IEXTJSColumn(interface.Interface):

    dataIndex = schema.Bytes(
                title=u'dataIndex',
                description=u"The name of the field in the grid's Ext.data.Store's Ext.data.Record definition from which to draw the column's value.",
                required=True)

    align = schema.Bytes(
                title=u'Align',
                description=u'Set the CSS text-align property of the column. Defaults to undefined.',
                default=None,
                required=False)

    css = schema.Bytes(
                title=u'Css',
                description=u'An inline style definition string which is applied to all table cells in the column (excluding headers).',
                default=None,
                required=False)

    css = schema.Bytes(
                title=u'Css',
                description=u'An inline style definition string which is applied to all table cells in the column (excluding headers).',
                default=None,
                required=False)

METADATA = {
    'root': 'rows',
    'totalProperty': 'totalCount',
    'fields': [],
    'columns': [],
}

FIELD = {'name': '', 'type': 'string'}
COLUMN = {'id':'','header': '', 'dataIndex': ''}

class Column(object):

    interface.implements(IEXTJSColumn)

    def __init__(self, **kwargs):

        for field in schema.getFields(IEXTJSColumn).values():
            if field.__name__ in kwargs:
                value = kwargs.get(field.__name__)
            else:
                value = field.default
            #bound = field.bind(self)
            #bound.validate(bound.get(self))
