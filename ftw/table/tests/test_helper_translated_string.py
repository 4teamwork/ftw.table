from ftw.table.helper import translated_string
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from unittest2 import TestCase


class TestTranslatedString(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def test_translate_unicode_string_returns_unicode(self):
        self.assertEqual(
            translated_string('ftw.table')(object, u'sortAscText'),
            u'sortAscText')

    def test_translate_none_returns_none_string(self):
        self.assertEqual(
            translated_string('ftw.table')(object, None),
            'None')

    def test_translate_utf8_string_returns_unicode(self):
        self.assertEqual(
            translated_string('ftw.table')(object, 'sortAscText'),
            u'sortAscText')
