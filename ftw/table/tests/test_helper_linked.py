from collections import namedtuple
from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import linked
from ftw.table.helper import linked_without_icon
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml.html import fromstring
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


SolrFlairMock = namedtuple('Flair',
                           ('Title', 'getIcon', 'portal_type'))


class TestLinkedWithIcon(TestCase):

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

    def test_has_link_if_called_with_a_brain(self):
        html = fromstring(linked(self.brain, self.brain.Title))

        self.assertEqual('a', html.find('a').tag)

    def test_has_link_with_obj(self):
        html = fromstring(linked(self.folder, self.folder.Title()))

        self.assertEqual('a', html.find('a').tag)

    def test_has_img_tag_in_link_tag(self):
        self.folder.getTypeInfo().icon_expr_object = Expression(
            'string:folder.jpg')
        self.folder.reindexObject()
        self.brain = getToolByName(self.portal, 'portal_catalog')(
            portal_type="Folder")[0]
        html = fromstring(linked(self.brain, self.brain.Title))

        self.assertEqual(1, len(html.xpath('a/img')))

    def test_img_src_to_obj_icon(self):
        self.folder.getTypeInfo().icon_expr_object = Expression(
            'string:folder.jpg')
        self.folder.reindexObject()
        self.brain = getToolByName(self.portal, 'portal_catalog')(
            portal_type="Folder")[0]

        html = fromstring(linked(self.brain, self.brain.Title))

        element = html.xpath('a/img')[0]

        self.assertEqual(
            '%s/folder.jpg' % self.portal.absolute_url(),
            element.attrib.get('src'))

    def test_link_text_is_obj_title(self):
        html = fromstring(linked(self.folder, self.folder.Title()))

        element = html.find('a')

        self.assertEqual(
            self.folder.Title(),
            element.text_content())

    def test_linked_with_unicode_title(self):
        # Solr flairs sometimes have unicode metadata..
        flair = SolrFlairMock(Title=u'\xf6rdnerli',
                              getIcon=u'file.png',
                              portal_type=u'File')
        self.assertIn(u'alt="\xf6rdnerli"',
                      linked(flair, flair.Title))


class TestLinkedWithoutIcon(TestCase):

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

    def test_has_link_if_called_with_a_brain(self):
        html = fromstring(linked_without_icon(self.brain, self.brain.Title))

        self.assertEqual('a', html.find('a').tag)

    def test_has_link_with_obj(self):
        html = fromstring(
            linked_without_icon(self.folder, self.folder.Title()))

        self.assertEqual('a', html.find('a').tag)

    def test_has_no_img_tag(self):
        html = fromstring(
            linked_without_icon(self.folder, self.folder.Title()))

        self.assertEqual([], html.xpath('a/img'))

    def test_link_text_is_obj_title(self):
        html = fromstring(
            linked_without_icon(self.folder, self.folder.Title()))

        element = html.find('a')

        self.assertEqual(
            self.folder.Title(),
            element.text_content())
