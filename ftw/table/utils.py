from interfaces import ITableGenerator
from zope.component import queryUtility
from  zope import interface
from zope import schema
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile 
from zope.app.component import hooks

class TableGenerator(object):
    """ generates a html table. See README.txt for usage"""
    
    template = ViewPageTemplateFile('templates/basic.pt') 
    
    _css_mapping = {
                   'table': 'listing',
                   'sortable': 'sortable', 
                   'sort-selected': 'sort-selected',
                   'sort-asc': 'sort-asc',
                   'sort-reverse': 'sort-reverse',
                   'th_prefix': 'header-'
                   }
    
    context = None
    @property
    def request(self):
     	site = hooks.getSite()
     	return site.REQUEST
    
    def generate(self, contents, columns, sortable=False, selected=(None,None), css_mapping={}, template=None):
        self.sortable = sortable
        self.selected = selected
        self.columns = self.process_columns(columns)
        self.contents = contents
        css = self._css_mapping.copy()
        css.update(css_mapping)
        self.css_mapping = css
        #if template is not None:
        #    #XXX dirty
        #    return template(**self.__dict__)
        return self.template()

    def get_value(self, content, column):
        attr, index, callback = column
        value = u''
        if hasattr(content, attr):
            value = getattr(content, attr)
        elif content.has_key(attr):
            value = content[attr]
        return callback(content, value)

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
        attr = index = u""
        callback = lambda x, y: y
        if isinstance(column, basestring):
            attr = index = column
        elif isinstance(column, (list, tuple)):
            if len(column) == 1:
                attr = index = column[0]
            elif len(column) == 2:
                if isinstance(column[1], basestring):
                    attr = column[0]
                    index = column[1]
                elif callable(column[1]):
                    attr = index = column[0]
                    callback = column[1]
            elif len(column) == 3:
                attr, index, callback = column
        return attr, index, callback
