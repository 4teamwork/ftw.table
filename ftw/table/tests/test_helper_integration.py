from ftw.table.helper import readable_author
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from lxml import html as parser
from plone.app.testing import TEST_USER_NAME, login, logout
from Products.CMFCore.utils import getToolByName
from time import time
from unittest2 import TestCase


class TestReadableAuthor(object):

    def register_user(self, user_id, fullname=''):
        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember(
            user_id,
            'password',
            properties=dict(
                username=user_id,
                fullname=fullname,
                email="t@t.ch"))

    def assert_link_attributes(self, html_link, url, text):
        # parser needs unicode to work correctly with umlauts
        html = parser.fromstring(html_link.decode('utf-8'))

        self.assertEquals(
            ['http://nohost/plone/author/%s' % url], html.values())

        self.assertEquals(text, html.text.encode('utf-8'))

    def set_allow_anonymous_view_about(self, enable):
        site_props = getToolByName(
            self.portal, 'portal_properties').site_properties
        site_props.allowAnonymousViewAbout = enable

    def test_default_sign_if_no_author_is_set(self):
        self.assertEquals('-', readable_author(None, ''))

    def test_not_linked_id_if_no_user_exists(self):
        self.assertEquals('james', readable_author(None, 'james'))


class TestReadableAuthorAnonymous(TestReadableAuthor, TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        logout()

    def test_not_linked_id_if_user_exists_with_no_fullname(self):
        self.set_allow_anonymous_view_about(False)
        self.register_user('olga')
        self.assertEquals('olga', readable_author(None, 'olga'))

    def test_not_linked_fullname_if_user_exists(self):
        self.set_allow_anonymous_view_about(False)
        self.register_user('bond', 'James Bond')
        self.assertEquals('James Bond', readable_author(None, 'bond'))

    def test_linked_id_if_user_exists_with_no_fullname_anonymous_allowed(self):
        self.set_allow_anonymous_view_about(True)
        self.register_user('lara')
        self.assert_link_attributes(
            readable_author(None, 'lara'), 'lara', 'lara')

    def test_linked_fullname_if_user_exists_and_anonymous_allowed(self):
        self.set_allow_anonymous_view_about(True)
        self.register_user('bud', 'Bud Spencer')
        self.assert_link_attributes(
            readable_author(None, 'bud'), 'bud', 'Bud Spencer')

    def test_umlauts_in_fullname(self):
        self.set_allow_anonymous_view_about(False)
        self.register_user('lara', 'Lara Cr\xc3\xb6ft')
        self.assertEquals('Lara Cr\xc3\xb6ft', readable_author(None, 'lara'))

    def test_caching(self):
        self.set_allow_anonymous_view_about(False)
        self.register_user('lara', 'Lara Croft')
        self.assertEquals('Lara Croft', readable_author(None, 'lara'))

        user = self.portal.portal_membership.getMemberById('lara')
        user.setMemberProperties(mapping={'fullname': 'James Bond'})

        # Caching blocks regetting the fullname and link
        self.assertEquals('Lara Croft', readable_author(None, 'lara'))


class TestReadableAuthorLoggedIn(TestReadableAuthor, TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)

    def test_linked_id_if_user_exists_with_no_fullname(self):
        self.register_user('olga')
        self.assert_link_attributes(
            readable_author(None, 'olga'), 'olga', 'olga')

    def test_linked_fullname_if_user_exists(self):
        login(self.portal, TEST_USER_NAME)
        self.register_user('bond', 'James Bond')
        self.assert_link_attributes(
            readable_author(None, 'bond'), 'bond', 'James Bond')

    def test_linked_if_anonymous_disallowed(self):
        self.register_user('lara')
        self.set_allow_anonymous_view_about(False)
        self.assert_link_attributes(
            readable_author(None, 'lara'), 'lara', 'lara')

    def test_umlauts_in_fullname(self):
        self.register_user('lara', 'Lara Cr\xc3\xb6ft')
        self.assert_link_attributes(
            readable_author(None, 'lara'), 'lara', 'Lara Cr\xc3\xb6ft')

    def test_caching(self):
        self.register_user('lara', 'Lara Croft')
        self.assert_link_attributes(
            readable_author(None, 'lara'), 'lara', 'Lara Croft')

        user = self.portal.portal_membership.getMemberById('lara')
        user.setMemberProperties(mapping={'fullname': 'James Bond'})

        # Caching blocks regetting the fullname and link
        self.assert_link_attributes(
            readable_author(None, 'lara'), 'lara', 'Lara Croft')

    def test_speed(self):
        self.register_user('speedy', 'Speedy Conzales')
        amount = 10000

        start = time()
        readable_author(None, 'speedy')
        end = time()
        time_without_cache = end - start

        # Test amount elements. Each should be faster than the first one
        load_start = time()
        for i in range(0, amount):
            readable_author(None, 'speedy')

        load_end = time()
        time_with_cache = load_end - load_start

        # Getting all readable authors should be
        # calculated in a responsible time
        self.assertTrue(
            time_without_cache*amount*0.2 > time_with_cache,
            "Caching should be 5 times faster than uncached values"
            " Time without: %s, time with: %s" % (
                time_without_cache*amount, time_with_cache))
