from interfaces import ITableGenerator
from zope.component import queryUtility
from  zope import interface
from zope import schema

#XXX: move to template
_u = lambda x: unicode(x, 'utf-8',errors='ignore')
TABLE = lambda x: u'<table class="listing" style="width:100%">%s</table>' % _u(x)
TR = lambda x: u"<tr>%s</tr>" % _u(x)
TD = lambda x: u"<td>%s</td>" % _u(x)
TH = lambda x, y: u"<td%s>%s</td>" % (_u(x), _u(y))

class TableGenerator(object):
    """ generates a html table"""
    
    def generate(self, contents, columns):
        rows = []
        if len(contents):
            #thead
            thead = []
            for column in columns:
                attr, index, callback = self.process_column(column)
                thead.append(TH(index, attr))
            rows.append(TR(' '.join(thead)))
            #tbody
            for content in contents:
                row = []
                for column in columns:
                    attr, index, callback = self.process_column(column)
                    row.append(TD(callback(getattr(content, attr, ''))))
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
                
         