from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import path_radiobutton
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml.html import fromstring
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestRadioButton(TestCase):

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

    def test_input_type_is_radio(self):
        html = fromstring(path_radiobutton(self.brain, None))

        self.assertEqual('radio', html.type)

    def test_title_has_prefix(self):
        html = fromstring(path_radiobutton(self.brain, None))

        self.assertEqual(
            'Select %s' % self.folder.Title(),
            html.attrib.get('title'))

    def test_is_not_checked_per_default(self):
        html = fromstring(path_radiobutton(self.brain, None))

        self.assertEqual(False, html.checked)

    def test_is_checket_if_url_is_in_request(self):
        self.brain.REQUEST.set(
            'paths', ['/'.join(self.folder.getPhysicalPath()), ])
        html = fromstring(path_radiobutton(self.brain, None))

        self.assertEqual(True, html.checked)
