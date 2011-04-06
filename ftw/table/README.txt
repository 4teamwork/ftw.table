Table Generator
===============

>>> from zope import component
>>> from ftw.table.interfaces import ITableGenerator
>>> generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
>>> generator
<ftw.table.utils.TableGenerator object at ...>

Generate a table from a list of dicts

>>> from datetime import datetime, timedelta
>>> today = datetime.today()
>>> employees = [
...                 {'name': 'Rincewind', 'date': datetime(today.year, today.month, today.day, 12, 30)},
...                 {'name': 'Ponder Stibbons', 'date': datetime(today.year, today.month, today.day, 11, 30)-timedelta(1)},
...                 {'name': 'The Librarian', 'date': datetime(2009,1,05, 17, 0)},
... ]
>>> columns = ('name', 'date')
>>> print generator.generate(employees, columns)
<table class="listing">
    <colgroup>
        <col class="col-name" />
        <col class="col-date" />
    </colgroup>
    <thead>
        <tr>
<BLANKLINE>
                <th id="header-name">
                    <span>name</span>
                </th>
<BLANKLINE>
<BLANKLINE>
                <th id="header-date">
                    <span>date</span>
                </th>
<BLANKLINE>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                Rincewind
            </td>
            <td>
                ...
            </td>
        </tr>
        <tr>
            <td>
                Ponder Stibbons
            </td>
            <td>
                ...
            </td>
        </tr>
        <tr>
            <td>
                The Librarian
            </td>
            <td>
                2009-01-05 17:00:00
            </td>
        </tr>
    </tbody>
</table>
<BLANKLINE>

Date doesn't look that pretty... use a helper to humanize it

>>> from ftw.table import helper
>>> columns = ('name', ('date', helper.readable_date_time_text))
>>> print generator.generate(employees, columns)
<table class="listing">
    ...
        <tr>
            <td> Rincewind </td>
            <td> heute, 12:30 </td>
        </tr>
        <tr>
            <td> Ponder Stibbons </td>
            <td> gestern, 11:30 </td>
        </tr>
        <tr>
            <td> The Librarian </td>
            <td> 05.01.2009 17:00 </td>
        </tr>
    ...
</table>

make your own helper.. E.g. to reverse the names

>>> def name_reverser(item, value):
...   """ A helper receives the current item and the value to modify"""
...   return value[::-1]
>>> columns1 = (('name', name_reverser), ('date', helper.readable_date))
>>> print generator.generate(employees, columns1)
<table class="listing">
    ...
            <td> dniwecniR </td>
    ...
</table>

# doesn't work atm and is not needed. Fix or discard later...
#generate columns from an Interface. needs some re-factoring/thinking.. not really useful atm.
#
# >>> from zope import interface, schema
# >>> class IEmployee(interface.Interface):
# ...     name = schema.Text(title=u"Name")
# ...     date = schema.Date(title=u"Date")
# >>> icolumns = IEmployee
# >>> print generator.generate(employees, icolumns)
# <table class="listing">
#     ...
#         <tr>
#                 <th id="header-date"> ... Date ... </th>
#                 <th id="header-name"> ... Name ... </th>
#         </tr>
#     ...
#         <tr>
#             <td> ... 12:30:00 </td>
#             <td> Rincewind </td>
#         </tr>
#     ...
# </table>

sortable tables
by default the table is not sortable

make all columns sortable

>>> sortable = True
>>> print generator.generate(employees, columns, sortable=sortable)
<table class="listing">
    ...
      <th id="header-name" class="sortable"> <span>name</span> </th>
      <th id="header-date" class="sortable"> <span>date</span> </th>
    ...
</table>

make only date sortable and define the currently selected column

>>> sortable = ('date', )
>>> selected = ('date','asc')
>>> print generator.generate(employees, columns, sortable=sortable, selected=selected)
<table class="listing">
    ...
      <th id="header-name"> ...
      <th id="header-date" class="sortable sort-selected sort-asc"> ...
    ...
</table>

You can overwrite/extend the the css_mapping. E.g. if you want to use swissgerman names

>>> css_mapping = {
...            'table': 'tabaeueli',
...            'sortable': 'sortierbar',
...            'sort-selected': 'dasda',
...            'sort-asc': 'ufe',
...            'sort-desc': 'abe',
...            'th_prefix': 'chopf'
...            }
>>> print generator.generate(employees, columns,
...                                     sortable=sortable,
...                                     selected=selected,
...                                     css_mapping=css_mapping)
<table class="tabaeueli">
...
                <th id="chopf-date"
                    class="sortierbar dasda ufe">...date...</th>
...
</table>

And now use it with plone.. and try it out with some more compley valuess

Create some test content

>>> generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
>>> books = [('Oblomow',  'Iwan A. Gontscharow'),
...            ('Cuentos de amor de locura y de muerte', 'Horacio Quiroga'),
...            ('Die grosse Haifischjagd', 'Hunter S. Thompson'),
...            ('Visual Intelligence', 'Donald D. Hoffman'),
...            ('Silence','John Cage'),
...            ('Small Gods', 'Terry Pratchett'),
...            ('How real is real?: Confusion; disinformation; communication', 'Paul Watzlawick')
...            ]
>>> from plone.i18n.normalizer.interfaces import IIDNormalizer
>>> normalize = component.getUtility(IIDNormalizer).normalize
>>> for book, author in books:
...     newid = self.folder.invokeFactory('Document', normalize(book), title=book, Description=author)
...     self.folder[newid].setDescription(author)
...     self.folder[newid].reindexObject()
>>> results = self.portal.portal_catalog(path={ 'depth':1, 'query':'/'.join(self.folder.getPhysicalPath())})
>>> columns = ('Title', 'Description', 'modified', 'Creator')

now we need some helpers and "simulate" the acl

>>> the_acl = {'test_user_1_' : 'The Librarian'}
>>> def checkbox(item, value):
...     return '<input type="checkbox" name="uids:list" value="%s" />' % item.UID
>>> def linked(item, value):
...     return '<a href="%s">%s</a>' % (item.getPath(), value)
>>> def readable_author(item, value):
...     return the_acl.get(value)
>>> columns = (('', checkbox),
...            ('Title', linked),
...            'Description',
...            ('modified', helper.readable_date_text),
...            ('Creator', readable_author))
>>> print generator.generate(results, columns)
<table class="listing">
...
        <tr>
            <td> <input type="checkbox" name="uids:list" value="..." /> </td>
            <td> <a href="/plone/Members/test_user_1_/die-grosse-haifischjagd">Die grosse Haifischjagd</a> </td>
            <td> Hunter S. Thompson </td>
            <td> heute... </td>
            <td> The Librarian </td>
        </tr>
...
</table>


Generate Table using a list of dicts.
>>> columns = [
...           {'transform' : checkbox},
...           {'column' : 'Title',
...            'column_title' : 'Title',
...            'sort_index' : 'sortable_title',
...            'transform' : linked},
...           {'column' : 'Description',
...            'column_title' : 'Author'},
...           {'column' : 'modified',
...            'transform' : helper.readable_date_text},
...           {'column' : 'Creator'}
... ]
>>> print generator.generate(results, columns)
<table class="listing">
        <colgroup>
            <col class="col" />
            <col class="col-sortable_title" />
            <col class="col-Description" />
            <col class="col-modified" />
            <col class="col-Creator" />
        </colgroup>
        <thead>
        <tr>
<BLANKLINE>
                <th id="header-checkbox">
<BLANKLINE>
                </th>
<BLANKLINE>
<BLANKLINE>
                <th id="header-sortable_title">
                    <span>Title</span>
                </th>
<BLANKLINE>
<BLANKLINE>
                <th id="header-Description">
                    <span>Author</span>
                </th>
<BLANKLINE>
<BLANKLINE>
                <th id="header-modified">
                    <span>modified</span>
                </th>
<BLANKLINE>
<BLANKLINE>
                <th id="header-Creator">
                    <span>Creator</span>
                </th>
<BLANKLINE>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <input type="checkbox" name="uids:list" value="..." />
            </td>
            <td>
                <a href="/plone/Members/test_user_1_/oblomow">Oblomow</a>
            </td>
            <td>
                Iwan A. Gontscharow
            </td>
            <td>
                heute
            </td>
            <td>
                test_user_1_
            </td>
        </tr>
        ...
    </tbody>
</table>

test list and dicts mixed up

>>> columns = [
...           ('Title', 'sortable_title', linked),
...           {'column' : 'Title',
...            'column_title' : 'Title',
...            'sort_index' : 'sortable_title',
...            'transform' : linked},]
>>> print generator.generate(results, columns)
<table class="listing">
    ...
        <col class="col-sortable_title" />
        <col class="col-sortable_title" />
    ...
        <th id="header-sortable_title">
            <span>Title</span>
        </th>
        <th id="header-sortable_title">
            <span>Title</span>
        </th>
    ...
        <td>
            <a href="/plone/Members/test_user_1_/silence">Silence</a>
        </td>
        <td>
            <a href="/plone/Members/test_user_1_/silence">Silence</a>
        </td>
    ...
</table>




