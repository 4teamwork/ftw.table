from ftw.builder import Builder
from ftw.builder import create
from ftw.table.helper import readable_author
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, login, logout
from Products.CMFCore.utils import getToolByName
from time import time
from unittest2 import TestCase


def set_allow_anonymous_view_about(context, enable):
    site_props = getToolByName(
        context, 'portal_properties').site_properties
    site_props.allowAnonymousViewAbout = enable


class TestReadableAuthor(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def test_default_sign_if_no_author_is_set(self):
        self.assertEquals('-', readable_author(object, ''))

    def test_not_linked_id_if_no_user_exists(self):
        self.assertEquals('james', readable_author(object, 'james'))


class TestReadableAuthorAnonymous(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        logout()

    def test_not_linked_id_if_user_exists_with_no_fullname(self):
        set_allow_anonymous_view_about(self.portal, False)
        create(Builder('user')).setMemberProperties(mapping={'fullname': ''})

        self.assertEquals('john.doe', readable_author(object, 'john.doe'))

    def test_not_linked_fullname_if_user_exists(self):
        set_allow_anonymous_view_about(self.portal, False)
        create(Builder('user'))
        self.assertEquals('Doe John', readable_author(object, 'john.doe'))

    def test_linked_id_if_user_exists_with_no_fullname_anonymous_allowed(self):
        set_allow_anonymous_view_about(self.portal, True)
        create(Builder('user')).setMemberProperties(mapping={'fullname': ''})

        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">john.doe</a>',
            readable_author(object, 'john.doe'))

    def test_linked_fullname_if_user_exists_and_anonymous_allowed(self):
        set_allow_anonymous_view_about(self.portal, True)
        create(Builder('user'))

        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">Doe John</a>',
            readable_author(object, 'john.doe'))

    def test_umlauts_in_fullname(self):
        set_allow_anonymous_view_about(self.portal, False)
        create(Builder('user').named('John', 'Tr\xc3\xa4volta'))

        self.assertEquals(
            'Tr\xc3\xa4Volta John', readable_author(object, 'john.tra-volta'))

    def test_caching(self):
        set_allow_anonymous_view_about(self.portal, False)
        user = create(Builder('user'))
        self.assertEquals('Doe John', readable_author(object, 'john.doe'))

        user.setMemberProperties(mapping={'fullname': 'James Bond'})

        # Caching blocks regetting the fullname and link
        self.assertEquals('Doe John', readable_author(object, 'john.doe'))


class TestReadableAuthorLoggedIn(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)

    def test_linked_id_if_user_exists_with_no_fullname(self):
        create(Builder('user')).setMemberProperties(mapping={'fullname': ''})
        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">john.doe</a>',
            readable_author(object, 'john.doe'))

    def test_linked_fullname_if_user_exists(self):
        login(self.portal, TEST_USER_NAME)
        create(Builder('user'))
        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">Doe John</a>',
            readable_author(object, 'john.doe'))

    def test_linked_if_anonymous_disallowed(self):
        create(Builder('user'))
        set_allow_anonymous_view_about(self.portal, False)
        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">Doe John</a>',
            readable_author(object, 'john.doe'))

    def test_umlauts_in_fullname(self):
        create(Builder('user').named('John', 'Tr\xc3\xa4volta'))
        self.assertEquals(
            '<a href="http://nohost/plone/author/john.tra-volta">'
            'Tr\xc3\xa4Volta John</a>',
            readable_author(object, 'john.tra-volta'))

    def test_caching(self):
        user = create(Builder('user'))
        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">Doe John</a>',
            readable_author(object, 'john.doe'))

        user.setMemberProperties(mapping={'fullname': 'James Bond'})

        # Caching blocks regetting the fullname and link
        self.assertEquals(
            '<a href="http://nohost/plone/author/john.doe">Doe John</a>',
            readable_author(object, 'john.doe'))

    def test_speed(self):
        create(Builder('user'))
        amount = 10000

        start = time()
        readable_author(object, 'john.doe')
        end = time()
        time_without_cache = end - start

        # Test amount elements. Each should be faster than the first one
        load_start = time()
        for i in range(0, amount):
            readable_author(object, 'john.doe')

        load_end = time()
        time_with_cache = load_end - load_start

        # Getting all readable authors should be
        # calculated in a responsible time
        self.assertTrue(
            time_without_cache * amount * 0.2 > time_with_cache,
            "Caching should be 5 times faster than uncached values"
            " Time without: %s, time with: %s" % (
                time_without_cache * amount, time_with_cache))
