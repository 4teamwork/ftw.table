from ftw.table.helper import readable_size
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from unittest2 import TestCase


class TestReadableSize(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def test_bytes(self):
        value = 555
        self.assertEqual(
            '555.0bytes',
            readable_size(object, value))

    def test_kbyte(self):
        value = 5555
        self.assertEqual(
            '5.4KB',
            readable_size(object, value))

    def test_mbyte(self):
        value = 5555555
        self.assertEqual(
            '5.3MB',
            readable_size(object, value))

    def test_gbyte(self):
        value = 5555555555
        self.assertEqual(
            '5.2GB',
            readable_size(object, value))

    def test_tbyte(self):
        value = 5555555555555
        self.assertEqual(
            '5.1TB',
            readable_size(object, value))

    def test_1023_is_the_last_byte_value(self):
        value = 1023
        self.assertEqual(
            '1023.0bytes',
            readable_size(object, value))

    def test_1024_is_the_first_kbyte_value(self):
        value = 1024
        self.assertEqual(
            '1.0KB',
            readable_size(object, value))

    def test_first_mbyte_value(self):
        value = 1048576
        self.assertEqual(
            '1.0MB',
            readable_size(object, value))

    def test_first_gbyte_value(self):
        value = 1073741824
        self.assertEqual(
            '1.0GB',
            readable_size(object, value))

    def test_first_tbyte_value(self):
        value = 1099511627776
        self.assertEqual(
            '1.0TB',
            readable_size(object, value))
