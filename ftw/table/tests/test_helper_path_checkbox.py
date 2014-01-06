from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import path_checkbox
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml.html import fromstring
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestCheckbox(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.folder = create(Builder('folder').titled(
            'the <"escaped"> Title').having(
            description='a <"f\xc3\xa4ncy"> description',
            ))

        self.brain = getToolByName(self.portal, 'portal_catalog')(
            portal_type="Folder")[0]

    def test_input_type_is_checkbox(self):
        html = fromstring(path_checkbox(self.brain, None))

        self.assertEqual('checkbox', html.type)

    def test_title_has_prefix(self):
        html = fromstring(path_checkbox(self.brain, None))

        self.assertEqual(
            'Select %s' % self.folder.Title(),
            html.attrib.get('title'))

    def test_value_is_path_to_object(self):
        html = fromstring(path_checkbox(self.brain, None))

        self.assertEqual(
            '/'.join(self.folder.getPhysicalPath()),
            html.attrib.get('value'))
