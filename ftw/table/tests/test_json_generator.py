from ftw.table.testing import FTWTABLE_ZCML_LAYER
from zope import component
from ftw.table.interfaces import ITableGenerator
from ftw.table.helper import readable_date_time
from zope.app.component.hooks import setSite
from plone.mocktestcase import MockTestCase
import json
from datetime import datetime, timedelta


COLUMNS_KEYS = ['dataIndex', 'header', 'id', 'sortable', ]

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

        # Some Test data
        today = datetime.today()
        self.employees = [
            {'name': 'Rincewind', 'date': datetime(
                today.year, today.month, today.day, 12, 30)},
            {'name': 'Ponder Stibbons', 'date': datetime(
                today.year,
                today.month,
                today.day,
                11, 30)-timedelta(1)},
            {'name': 'The Librarian', 'date': datetime(
                2009, 1, 05, 17, 0)}, ]
        # for JSON output datetime objects are no supportet, so transform it
        self.columns = [
                  {'column': 'name',
                   'column_title': 'NAME',
                   'sort_index': 'sortable_name',
                   },
                  {'column': 'date',
                   'column_title': 'DATE',
                   'sort_index': 'sortable_date',
                   'transform': readable_date_time
                   }]



    def json_output(self):
        """generates a table from a list of dicts"""
        generator = component.getUtility(ITableGenerator, 'ftw.tablegenerator')


        return generator.generate(self.employees, self.columns, output='json')


    def test_json_string_output(self):
        self.assertTrue(isinstance(self.json_output(), str))

    def test_json_decode(self):
        data = self.json_output()
        self.assertTrue(isinstance(
            json.loads(data),
            dict))

    def test_totalCount(self):
        data = json.loads(self.json_output())
        total_count_property = data['metaData']['totalProperty']
        self.assertEquals(data[total_count_property], len(data['rows']))

    def test_rows_values(self):
        # Just check if there is some data
        # Porcess columns and tranformations are already tested
        data = json.loads(self.json_output())
        rows = data['rows']
        self.assertEquals(len(rows), 3) # 3 employees
        # Test first entry - unicode and not empty
        self.assertTrue(isinstance(
            rows[0]['sortable_date'],
            unicode))
        self.assertFalse(rows[0]['sortable_date'] == u'')
        self.assertTrue(isinstance(
            rows[0]['sortable_name'],
            unicode))
        self.assertFalse(rows[0]['sortable_name'] == u'')
        # Test second entry - unicode and not empty
        self.assertTrue(isinstance(
            rows[1]['sortable_date'],
            unicode))
        self.assertFalse(rows[1]['sortable_date'] == u'')
        self.assertTrue(isinstance(
            rows[1]['sortable_name'],
            unicode))
        self.assertFalse(rows[1]['sortable_name'] == u'')
        # Test third entry - unicode and not empty
        self.assertTrue(isinstance(
            rows[2]['sortable_date'],
            unicode))
        self.assertFalse(rows[2]['sortable_date'] == u'')
        self.assertTrue(isinstance(
            rows[2]['sortable_name'],
            unicode))
        self.assertFalse(rows[2]['sortable_name'] == u'')

    def test_missing_value(self):
        # Broken brain values should result in an empty string
        import Missing
        self.employees[0]['name'] = Missing.Value
        data = json.loads(self.json_output())
        self.assertEquals(
            data['rows'][0]['sortable_name'], u'')

    def test_column_data_structure(self):
        # A Column should contain a dict with the following keys
        data = json.loads(self.json_output())
        for column in data['metaData']['columns']:
            for name in COLUMNS_KEYS:
                self.assertTrue(name in column)

    def test_translate_column_title(self):
        # XXX: This test doesn't work so far
        from zope.i18nmessageid import MessageFactory
        factory = MessageFactory('plone')
        self.columns[0]['column_title'] = factory(u'TRANSLATE_NAME')
        data = json.loads(self.json_output())
        self.assertEquals(
            data['metaData']['columns'][0]['header'],
            'TRANSLATE_NAME')

    def test_group_data(self):
        # XXX Implement me
        pass