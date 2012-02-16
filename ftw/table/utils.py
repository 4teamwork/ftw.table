from  zope import interface
from zope import schema
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.component import hooks
from zope.i18nmessageid.message import Message
from zope.i18n import translate
from column import METADATA, FIELD, COLUMN
from copy import deepcopy
import Missing

try:
    import json
except ImportError:
    import simplejson as json


class TableGenerator(object):
    """ generates a html table. See README.txt for usage"""

    template = ViewPageTemplateFile('templates/basic.pt')

    _css_mapping = {
                   'table': 'listing',
                   'sortable': 'sortable',
                   'sort-selected': 'sort-selected',
                   'sort-asc': 'sort-asc',
                   'sort-reverse': 'sort-reverse',
                   'th_prefix': 'header',
                   'no_sortable': 'nosort'}


    #msgids of strings that will be used in the GridView. domain=ftw.table
    _translations = ['sortDescText', 'sortAscText', 'columnsText',
                   'showGroupsText', 'groupByText', 'itemsPlural',
                   'itemsSingular', 'selectedRowen', 'dragDropLocked']

    context = None

    @property
    def request(self):
        site = hooks.getSite()
        return site.REQUEST

    @property
    def site(self):
        return hooks.getSite()

    def generate(self, contents, columns, sortable=False,
                 selected=(None, None), css_mapping={}, translations=[],
                 template=None, options={}, output='html', meta_data=None):
        self.sortable = sortable
        self.selected = selected
        self.columns = self.process_columns(columns)
        self.contents = contents
        self.options = options
        self.grouping_enabled = False

        if output == 'html':
            # XXX
            # NOT WORK, WHEN WE USED THE TRANSFERRED TEMPLATE
            if template is not None:
                self.template = ViewPageTemplateFile(template.filename)
            css = self._css_mapping.copy()
            css.update(css_mapping)
            self.css_mapping = css
            #if template is not None:
            #    #XXX dirty
            #    return template(**self.__dict__)
            return self.template(self)
        elif output == 'json':

            msgids = set(self._translations + translations)

            table = dict(totalCount = len(self.contents),
                        rows = [])

            for content in self.contents:
                row = {}
                if isinstance(content, tuple):
                    # group is enabled.
                    # when group is enabled, the rows should be tuples
                    # containg the group label
                    if not isinstance(content, tuple):
                        raise ValueError('Expected row to be a tuple since '
                                         'grouping is activated.')
                    self.grouping_enabled = True
                    content, row['groupBy'] = content

                for column in self.columns:
                    key = (column.get('sort_index', None) or
                            column['attr'] or
                            column['title'] or
                            column['transform'].__name__)

                    value = self.get_value(content, column)
                    if value == Missing.Value:
                        value = ''
                    if isinstance(value, Message):
                        value = translate(value,
                                          domain='ftw.table',
                                          context=self.context)
                    row[key] = value
                    try:
                        row['id'] = content.id
                    except AttributeError:
                        pass
                table['rows'].append(row)


            if meta_data is None:
                #create metadata for oldstyle column definition
                meta_data = deepcopy(METADATA)
                for column in self.columns:

                    key = (column.get('sort_index', None) or
                            column['attr'] or
                            column['title'] or
                            column['transform'].__name__)

                    field = deepcopy(FIELD)
                    field['name'] = key
                    col = deepcopy(COLUMN)
                    col['dataIndex'] = key
                    if isinstance(column['title'], Message):
                        col['header'] = translate(column['title'],
                                                  column['title'].domain,
                                                  context = self.request)
                    else:
                        col['header'] = column['title']
                    col['id'] = key
                    if not column['title']:
                        if key == 'draggable':
                            col['menuDisabled'] = False
                            col['header'] = '&nbsp;'
                            col['sortable'] = True
                        else:
                            col['menuDisabled'] = True
                        col['width'] = 30
                        col['hideable'] = False
                        col['resizable'] = False
                        col['fixed'] = True
                    else:
                        col['sortable'] = True
                    meta_data['fields'].append(field)
                    meta_data['columns'].append(col)

                meta_data['config'] = {}
                # if grouping is enabled add additional column
                if self.grouping_enabled:
                    col = deepcopy(COLUMN)
                    field = deepcopy(FIELD)
                    meta_data['config']['group'] = field['name'] = \
                        col['dataIndex'] = col['header'] = \
                        col['id'] = 'groupBy'
                    col['sortable'] = False
                    col['hideable'] = False
                    meta_data['fields'].append(field)
                    meta_data['columns'].append(col)

                meta_data['config']['gridstate'] = options.get(
                    'gridstate', None)
                meta_data['config']['sort'] = selected[0]
                sort_order = selected[1]
                if sort_order is None:
                    sort_order = 'asc'
                elif sort_order == 'reverse':
                    sort_order = 'desc'
                meta_data['config']['dir'] = sort_order.upper()
                if self.options and 'auto_expand_column' in self.options:
                    aecolumn = self.options['auto_expand_column']
                    meta_data['config']['auto_expand_column'] = aecolumn

            #add static html snippets. Eg batching, buttons, etc
            if 'static' in self.options:
                meta_data['static'] = deepcopy(self.options['static'])

            #add translations for the table
            meta_data['translations'] = {}
            for msgid in msgids:
                meta_data['translations'][msgid] = translate(msgid,
                                                        domain='ftw.table',
                                                        context=self.request)
            if meta_data:
                table['metaData'] = meta_data
            jsonstr = json.dumps(table)
            return jsonstr
        else:
            return 'unsupported output format'

    def get_value(self, content, column):
        attr = column['attr']
        transform = column['transform']

        value = u''
        if hasattr(content, attr):
            value = getattr(content, attr)
        elif hasattr(content, '__iter__') and attr in content:
            value = content[attr]
        return transform(content, value)

    def sortable_class(self, attr):
        class_ = []
        if isinstance(self.sortable, (bool, int)):
            #if sortable is set to True, everything is sortable
            if self.sortable:
                class_.append(self.css_mapping['sortable'])
        elif attr in self.sortable:
            class_.append(self.css_mapping['sortable'])
        else:
            class_.append(self.css_mapping['no_sortable'])
        if len(class_):
            if attr == self.selected[0]:
                class_.append(self.css_mapping['sort-selected'])
                name = 'sort-' + self.selected[1]
                if name in self.css_mapping:
                    class_.append(self.css_mapping[name])
            return ' '.join(class_)
        return None

    def get_thid(self, column):
        id_ = None
        attr = column['sort_index']
        if len(attr):
            id_ = attr
        elif 'transform' in column:
            name = column['transform'].__name__
            if name != '<lambda>':
                id_ = name
        if id_ is not None:
            return '%s-%s' % (self.css_mapping['th_prefix'], id_)
        return id_

    def process_columns(self, columns):
        processed_columns = []
        if isinstance(columns, (list, tuple)):
            for column in columns:
                col = self.process_column(column)
                if col is not None:
                    processed_columns.append(col)

        elif type(columns) == type(interface.Interface):
            column = []
            fields = schema.getFields(columns).items()
            for name, field in fields:
                col = self.process_column((field.title, name))
                if col is not None:
                    processed_columns.append(col)

        return processed_columns

    def process_column(self, column):
        attr = sort_index = title = u""
        transform = lambda x, y: y
        if isinstance(column, basestring):
            attr = sort_index = column

        elif isinstance(column, (list, tuple)):
            if len(column) == 1:
                attr = sort_index = column[0]

            elif len(column) == 2:
                if isinstance(column[1], basestring):
                    attr = column[0]
                    sort_index = column[1]
                elif callable(column[1]):
                    attr = sort_index = column[0]
                    transform = column[1]

            elif len(column) == 3:
                attr, sort_index, transform = column

        elif isinstance(column, dict):
            # skip column if condition function returns False
            condition = column.get('condition', None)
            if callable(condition) and condition() == False:
                return None

            attr = column.get('column', attr)
            title = column.get('column_title', title)
            sort_index = column.get('sort_index', sort_index)
            transform = column.get('transform', transform)

        title = len(title) and title or attr
        sort_index = len(sort_index) and sort_index or attr

        #return attr, sort_index, transform
        return {'attr': attr,
                'title': title,
                'sort_index': sort_index,
                'transform': transform}
