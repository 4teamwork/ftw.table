from ftw.builder import Builder
from ftw.builder import create
from ftw.table.catalog_source import DefaultCatalogTableSourceConfig
from ftw.table.interfaces import ITableSource
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestCatalogSource(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        super(TestCatalogSource, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.folder = create(Builder('folder').titled('Hanspeter'))
        self.config = DefaultCatalogTableSourceConfig()
        self.config.request = self.portal.REQUEST
        self.source = getMultiAdapter((self.config, self.portal.REQUEST),
                                      ITableSource)

    def _execute_query(self, filter_text):
        self.config.filter_text = filter_text
        query = self.source.build_query()
        return self.source.search_results(query)

    def test_searching_special_chars_only_returns_empty_result(self):
        self.assertSequenceEqual([], self._execute_query('***'))
        self.assertSequenceEqual([], self._execute_query('%&$*#&'))

    def test_searching_unmatched_parenthesis_returns_emtpy_result(self):
        self.assertSequenceEqual([], self._execute_query('(blahh'))

    def test_searching_text_returns_folder(self):
        self.assertSequenceEqual(
            [self.folder],
            [each.getObject() for each in self._execute_query('Hanspeter')])
