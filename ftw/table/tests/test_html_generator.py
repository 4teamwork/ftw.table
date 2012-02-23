from ftw.table.testing import FTWTABLE_ZCML_LAYER
from zope import component
from ftw.table.interfaces import ITableGenerator
from ftw.table.utils import TableGenerator
import re
from zope.app.component.hooks import setSite
from xml.dom.minidom import parseString
from plone.mocktestcase import MockTestCase


def cleanup_whitespace(html):
    """replace multiple whitespaces with one single space
    """
    return re.sub('\s{2,}', ' ', html)


class TestHTMLTableGenerator(MockTestCase):

    layer = FTWTABLE_ZCML_LAYER

    def setUp(self):
        self.site = self.mocker.mock(count=False)
        self.request = self.mocker.mock(count=False)
        self.response = self.mocker.mock(count=False)

        setSite(self.site)
        self.expect(self.site.REQUEST).result(self.request)
        self.expect(self.request.debug).result(False)
        self.expect(self.request.response).result(self.response)
        self.expect(self.response.getHeader('Content-Type')).result('text/html')

        self.replay()

    def test_generator_utility(self):
        """Get Utility"""
        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        self.assertTrue(generator, TableGenerator)

    def test_list_of_dicts(self):
        """generates a table from a list of dicts"""
        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        from datetime import datetime, timedelta
        today = datetime.today()
        employees = [
            {'name': 'Rincewind', 'date': datetime(
                today.year, today.month, today.day, 12, 30)},
            {'name': 'Ponder Stibbons', 'date': datetime(
                today.year,
                today.month,
                today.day,
                11, 30)-timedelta(1)},
            {'name': 'The Librarian', 'date': datetime(
                2009, 1, 05, 17, 0)},
        ]
        columns = ('name', 'date')
        html_output = generator.generate(employees, columns)

        # Use minidom to verify the generates html
        parsed = parseString(html_output)
        table = parsed.getElementsByTagName('table')

        # only one table node
        self.assertEqual(len(table), 1)

        # check table node itself
        table = table[0]
        self.assertEqual(table.tagName, u'table')
        # Table has a class named "listing"
        self.assertEqual(table._attrs['class'].nodeValue, 'listing')

        # Two columns
        th = parsed.getElementsByTagName('th')
        self.assertEqual(len(th), 2)

        # th contain a span tag with the column title
        th1 = th[0]
        th2 = th[1]
        self.assertEqual(th1._attrs['id'].nodeValue, u'header-name')
        self.assertEqual(th2._attrs['id'].nodeValue, u'header-date')

        self.assertEqual(
            th1.getElementsByTagName('span')[0].childNodes[0].data,
            u'name')
        self.assertEqual(
            th2.getElementsByTagName('span')[0].childNodes[0].data,
            u'date')

        # three records with name and date (skip first row)
        rows = parsed.getElementsByTagName('tr')
        self.assertEqual(len(rows), 4)
        td11, td12 = rows[1].getElementsByTagName('td')
        self.assertTrue('Rincewind' in td11.childNodes[0].data)
        self.assertTrue(str(today.year) in td12.childNodes[0].data)

        td21, td22 = rows[2].getElementsByTagName('td')
        self.assertTrue('Ponder Stibbons' in td21.childNodes[0].data)
        self.assertTrue(str(today.year) in td22.childNodes[0].data)

        td31, td32 = rows[3].getElementsByTagName('td')
        self.assertTrue('The Librarian' in td31.childNodes[0].data)
        self.assertTrue('2009' in td32.childNodes[0].data)

    def test_sortable_columns(self):
        """Make columns sortable:
        - All columns
        - Only specific columns"""
        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        employees = [
            {'name': 'some name', 'date': 'somedate'},
        ]
        columns = ('name', 'date')
        parsed = parseString(
            generator.generate(employees, columns, sortable=True))
        # Sortable=True adds a class sortable to all table headers
        self.assertEqual(
            parsed.getElementsByTagName('th')[0]._attrs['class'].nodeValue,
            'sortable')
        self.assertEqual(
            parsed.getElementsByTagName('th')[1]._attrs['class'].nodeValue,
            'sortable')

        # Add sortable class only on column 'name', all other has a nosort class
        columns = ('name', 'date')
        sortable = ('name', )
        parsed = parseString(
            generator.generate(employees, columns, sortable=sortable))
        self.assertEqual(
            parsed.getElementsByTagName('th')[0]._attrs['class'].nodeValue,
            'sortable')
        self.assertEqual(
            parsed.getElementsByTagName('th')[1]._attrs['class'].nodeValue,
            u'nosort')

    def test_init_sort_direction_column(self):
        """Make columns sortable and set init
        sort column and direction"""
        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        employees = [
            {'name': 'some name', 'date': 'somedate'},
        ]
        columns = ('name', 'date')
        selected = ('name', 'asc')
        parsed = parseString(
            generator.generate(
                employees, columns, sortable=True, selected=selected))

        self.assertEqual(
            parsed.getElementsByTagName('th')[0]._attrs['class'].nodeValue,
            'sortable sort-selected sort-asc')

    def test_css_mappings(self):
        """It's possible to use your own css classes"""

        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        employees = [
            {'name': 'some name', 'date': 'somedate'},
        ]
        columns = ('name', 'date')
        selected = ('name', 'asc')

        # use alternate css classes
        css_mapping = {
                'table': 'CustomTableClass',
                'sortable': 'CustomSortableClass',
                'sort-selected': 'CustomSelectedClass',
                'sort-asc': 'CustomUpClass',
                'sort-desc': 'CustomDownClass',
                'th_prefix': 'custom-header-prefix'}

        # We do not use minidom to parse. Just check if the given html snippeds
        # are available
        html = generator.generate(
            employees,
            columns,
            sortable=True,
            selected=selected,
            css_mapping=css_mapping)
        self.assertTrue('<table class="CustomTableClass">' in html)
        self.assertIn(
            '<th id="custom-header-prefix-name" '
            'class="CustomSortableClass CustomSelectedClass '
            'CustomUpClass">', cleanup_whitespace(html))

        # Test also sort-desc css class mapping with a new generated table
        columns = ('name', 'date')
        selected = ('date', 'desc')
        html = generator.generate(
            employees,
            columns,
            sortable=True,
            selected=selected,
            css_mapping=css_mapping)
        self.assertIn(
            '<th id="custom-header-prefix-date" class="CustomSortableClass '
            'CustomSelectedClass CustomDownClass">', cleanup_whitespace(html))

    def test_column_definition_tuple_dict(self):
        """Generate table headers using a dict and a tuple"""

        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        employees = [
            {'name': 'some name', 'date': 'somedate', 'info': 'someinfo'},
        ]


        columns = [
                  {'column': 'name',
                   'column_title': 'NAME',
                   'sort_index': 'sortable_name'},
                   ('date', 'sortable_date'),  # not so readable
                   ('info', )]

        html = generator.generate(employees, columns)
        # generates col tags
        self.assertTrue('<col class="col-sortable_name" />' in html)
        self.assertTrue('<col class="col-sortable_date" />' in html)

        # The correct id on table headers
        self.assertTrue('<th id="header-sortable_name">' in html)
        self.assertTrue('<th id="header-sortable_date">' in html)

        # look for capitalized table column title
        parsed = parseString(html)
        self.assertEqual(
            parsed.getElementsByTagName('th')[0].childNodes[1]\
                .childNodes[0].data,
            'NAME')

    def test_column_transform(self):
        """Transform table data"""

        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        employees = [
            {'name': 'some name', 'date': 'somedate'},
        ]

        def string_reverser(item, value):
            """ A helper receives the current item and the value to modify"""
            return value[::-1]


        columns = [
                  {'column': 'name',
                   'column_title': 'NAME',
                   'sort_index': 'sortable_name',
                   'transform': string_reverser},
                   ('date', 'sortable_date', string_reverser)]

        html = generator.generate(employees, columns)
        self.assertTrue('eman emos' in html)
        self.assertTrue('etademos' in html)

    def test_column_condition(self):
        """It's possible to hide columns by a given condition
        Only in dict representation possible"""

        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')
        employees = [
            {'name': 'some name', 'date': 'somedate'},
        ]

        def dummy_condition():
            return False
        columns = [
                  {'column': 'name',
                   'column_title': 'NAME',
                   'sort_index': 'sortable_name',
                   'condition': dummy_condition},
                   ('date', 'sortable_date', )]

        html = generator.generate(employees, columns)
        self.assertFalse('<th id="header-sortable_name">' in html)
