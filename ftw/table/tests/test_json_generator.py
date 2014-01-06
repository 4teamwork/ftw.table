from datetime import datetime
from datetime import timedelta
from ftw.table.helper import readable_date_time
from ftw.table.interfaces import ITableGenerator
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from unittest2 import TestCase
from zope import component
import json


COLUMNS_KEYS = ['dataIndex', 'header', 'id', 'sortable', ]


class TestJsonGenerator(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):

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
                'sort_index': 'sortable_name'},
            {'column': 'date',
                'column_title': 'DATE',
                'sort_index': 'sortable_date',
                'transform': readable_date_time}]

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
        # 3 employees
        self.assertEquals(len(rows), 3)
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
