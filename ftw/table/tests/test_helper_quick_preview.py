from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import quick_preview
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml.html import fromstring
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestQuickPreview(TestCase):

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

    def test_has_linkwrapper(self):
        html = fromstring(quick_preview(self.brain, self.brain.Title))

        self.assertEqual('linkWrapper', html.attrib.get('class'))
        self.assertEqual('span', html.tag)

    def test_has_link_in_wrapper(self):
        html = fromstring(quick_preview(self.brain, self.brain.Title))
        element = html.xpath('a')

        self.assertTrue(1, len(element))

    def test_link_tag_class_is_set(self):
        html = fromstring(quick_preview(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual('quick_preview', element.attrib.get('class'))

    def test_set_href_to_preview_with_brain(self):
        html = fromstring(quick_preview(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(
            '%s/quick_preview' % self.folder.absolute_url(),
            element.attrib.get('href'))

    def test_set_href_to_preview_with_obj(self):
        html = fromstring(quick_preview(self.folder, self.folder.Title()))
        element = html.find('a')

        self.assertEqual(
            '%s/quick_preview' % self.folder.absolute_url(),
            element.attrib.get('href'))

    def test_link_text_is_context_title(self):
        html = fromstring(quick_preview(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(
            self.folder.Title(),
            element.text_content())

    def test_has_img_attribute_in_a_tag(self):
        html = fromstring(quick_preview(self.brain, self.brain.Title))
        element = html.xpath('a/img')

        self.assertTrue(1, len(element))
        self.assertEqual('img', element[0].tag)

    def test_img_scr_to_context_icon_if_icon_exists(self):
        self.folder.getTypeInfo().icon_expr_object = Expression(
            'string:folder.jpg')
        self.folder.reindexObject()
        self.brain = getToolByName(self.portal, 'portal_catalog')(
            portal_type="Folder")[0]

        html = fromstring(quick_preview(self.brain, self.brain.Title))
        element = html.xpath('a/img')[0]

        self.assertEqual(
            '%s/folder.jpg' % self.portal.absolute_url(),
            element.attrib.get('src'))
