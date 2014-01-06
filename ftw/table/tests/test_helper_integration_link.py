from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import link
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml.html import fromstring
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestLink(TestCase):

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

    def add_content_type_icon(self):
        self.folder.getTypeInfo().icon_expr_object = Expression(
            'string:folder.jpg')
        self.folder.reindexObject()
        self.brain = getToolByName(self.portal, 'portal_catalog')(
            portal_type="Folder")[0]

    def test_works_with_brain_and_object(self):
        self.assertEqual(
            link()(self.brain, self.brain.Title),
            link()(self.folder, self.folder.Title()))

    def test_link_text_is_object_title(self):
        html = fromstring(link()(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(self.folder.Title(), element.text)

    def test_link_href_is_object_url(self):
        html = fromstring(link()(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(
            self.folder.absolute_url(),
            element.attrib.get('href'))

    def test_link_with_icon_if_no_icon_exists_adds_css_class(self):
        html = fromstring(link(icon=True)(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(
            'contenttype-%s' % self.folder.portal_type.lower(),
            element.attrib.get('class'))

    def test_link_with_icon_add_img_attribute(self):
        self.add_content_type_icon()
        html = fromstring(link(icon=True)(self.brain, self.brain.Title))

        element = html.find('a/img')

        self.assertEqual(
            "%s/folder.jpg" % self.portal.absolute_url(),
            element.attrib.get('src'))

    def test_link_without_icon_has_no_class_and_no_img_attribute(self):
        html = fromstring(link(icon=False)(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(['href'], element.attrib.keys())
        self.assertEqual(None, element.find('img'))

    def test_link_with_tooltips(self):
        html = fromstring(link(
            icon=False, tooltip=True)(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual('rollover', element.attrib.get('class'))
        self.assertEqual(
            self.folder.Description(),
            element.attrib.get('title').encode('utf-8'))

    def test_link_classes(self):
        html = fromstring(
            link(icon=False, classes=['foo', 'bar'])(
                self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual('bar foo', element.attrib.get('class'))

    def test_link_attrs(self):
        html = fromstring(
            link(attrs={'name': 'fo\xc3\xb6'})(self.brain, self.brain.Title))
        element = html.find('a')

        self.assertEqual(u'fo\xf6', element.attrib.get('name'))

    def test_link_icon_only(self):
        self.add_content_type_icon()
        html = fromstring(
            link(icon=True, icon_only=True)(self.brain, self.brain.Title))

        element = html.find('a')

        self.assertEqual(None, element.text)
        self.assertEqual(
            "%s/folder.jpg" % self.portal.absolute_url(),
            element.find('img').attrib.get('src'))
