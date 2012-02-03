from  ftw.table.testing import FTWTABLE_ZCML_LAYER
from plone.mocktestcase import MockTestCase
from zope import component
from ftw.table.interfaces import ITableGenerator
from ftw.table.utils import TableGenerator


class TestTableGenerator(MockTestCase):

    layer = FTWTABLE_ZCML_LAYER

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
            {'name': 'Rincewind', 'date': datetime(today.year, today.month, today.day, 12, 30)},
            {'name': 'Ponder Stibbons', 'date': datetime(today.year, today.month, today.day, 11, 30)-timedelta(1)},
            {'name': 'The Librarian', 'date': datetime(2009,1,05, 17, 0)},
        ]
        columns = ('name', 'date')
        generator.generate(employees, columns)
        import ipdb; ipdb.set_trace()