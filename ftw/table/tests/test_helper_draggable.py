from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import draggable
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml.html import fromstring
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestDragable(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.folder = create(Builder('folder'))
        self.brain = getToolByName(self.portal, 'portal_catalog')(
            portal_type="Folder")[0]

    def test_id_with_prefix_draggable(self):
        html = fromstring(draggable(self.brain, None))

        self.assertEqual(
            "draggable-%s" % self.folder.getId(),
            html.attrib.get('id'))

    def test_has_css_class_draggable(self):
        html = fromstring(draggable(self.brain, None))

        self.assertEqual(
            "draggable", html.attrib.get('class'))
