from  zope import interface
from zope import schema
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile 
from zope.app.component import hooks

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
                   'th_prefix': 'header'
                   }
    
    context = None
    @property
    def request(self):
     	site = hooks.getSite()
     	return site.REQUEST
    
    def generate(self, contents, columns, sortable=False, 
                 selected=(None,None), css_mapping={}, 
                 template=None, auto_count=None, output='html'):
        self.sortable = sortable
        self.selected = selected
        self.columns = self.process_columns(columns)
        self.contents = contents
        self.auto_count = auto_count
        # TODO: implement json support
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
            table = dict(totalCount = len(self.contents),
                        rows = []
                    )
            for content in self.contents:
                row = {}
                for column in self.columns:
                    key =  (column['attr'] or 
                            column['title'] or 
                            column['transform'].__name__)
                    value = self.get_value(content, column)
                    row[key] = value
                table['rows'].append(row)
                return json.dumps(table)
            pass
        else:
            return 'unsupported output format'
            

    def get_value(self, content, column):
        attr = column['attr']
        sort_index = column['sort_index']
        transform = column['transform']
        
        value = u''
        if hasattr(content, attr):
            value = getattr(content, attr)
        elif content.has_key(attr):
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
        if len(class_):
            if attr == self.selected[0]:
                class_.append(self.css_mapping['sort-selected'])
                name = 'sort-' + self.selected[1]
                if self.css_mapping.has_key(name):
                    class_.append(self.css_mapping[name])
            return ' '.join(class_)
        return None

    def get_thid(self, column):
        id_ = None
        attr = column['sort_index']
        if len(attr):
            id_ = attr
        elif column.has_key('transform'):
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
                processed_columns.append(self.process_column(column))
        elif type(columns) == type(interface.Interface):
            column = []
            fields = schema.getFields(columns).items()
            for name, field  in fields:
                processed_columns.append(self.process_column((field.title, name)))
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
            attr = column.get('column', attr)
            title = column.get('column_title', title)
            sort_index = column.get('sort_index', sort_index)
            transform = column.get('transform', transform)

        title = len(title) and title or attr
        sort_index = len(sort_index) and sort_index or attr
        
        #return attr, sort_index, transform        
        return {'attr':attr, 'title':title , 'sort_index':sort_index, 'transform': transform}
    
        