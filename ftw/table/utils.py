from interfaces import ITableGenerator
from zope.component import queryUtility
from  zope import interface
from zope import schema

#XXX: move to template or use pyquery?
TABLE = lambda x: u'<table class=\'sortable-table\'>%s</table>' % x
TR = lambda x: u"<tr>%s</tr>" % x
TD = lambda x: u"<td>%s</td>" % x
TH = lambda x, y: u"<th id=\'%s\' class=\'sortable\'><span>%s</span></th>" % (x,y)
A = lambda x, y: "<a href=\'%s\'>%s</a>" % (x,y)

class TableGenerator(object):
    """ generates a html table"""
    
    def generate(self, contents, columns, linked):
        rows = []
        if len(contents):
            #thead
            thead = []
            thead.append(TH('','<span></span>  '))
            for column in columns:
                attr, index, callback = self.process_column(column)
                thead.append(TH(index, attr))
            rows.append(TR(' '.join(thead)))
            #tbody
            for content in contents:
                row = []
                row.append(TD('<input type=\'checkbox\' />'))
                for column in columns:
                    attr, index, callback = self.process_column(column)
                    value = callback(getattr(content, attr, ''))
                    if attr in linked:
                        value = A(content.getURL(), value)
                    row.append(TD(value))
                rows.append(TR(' '.join(row)))
            return TABLE(' '.join(rows))
                        
    def process_column(self, column):
        attr = index =""
        callback = lambda x: x
        if len(column) == 1:
            attr = index = column
        if len(column) == 2:
            attr, index = column
        if len(column) == 3:
            attr, index, callback = column
        return attr, index, callback
                
         