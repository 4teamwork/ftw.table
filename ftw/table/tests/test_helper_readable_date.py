from datetime import datetime
from datetime import time
from datetime import timedelta
from ftw.table.helper import readable_date
from ftw.table.helper import readable_date_text
from ftw.table.helper import readable_date_time
from ftw.table.helper import readable_date_time_text
from ftw.table.testing import FTWTABLE_INTEGRATION_TESTING
from unittest2 import TestCase


class TestReadableDate(TestCase):

    layer = FTWTABLE_INTEGRATION_TESTING

    def test_empty_string_if_no_value_is_given(self):
        self.assertEqual(
            u'',
            readable_date(object, None))

    def test_none_if_value_is_invalid(self):
        self.assertEqual(
            None,
            readable_date(object, 'invalid date'))

    def test_date_in_format_d_m_y(self):
        self.assertEqual(
            '17.10.2012',
            readable_date(object, datetime(2012, 10, 17, 20, 8)))


class TestReadableDateTime(TestCase):

    def test_none_if_no_value_is_given(self):
        self.assertEqual(
            None,
            readable_date_text(object, None))

    def test_none_if_value_is_invalid(self):
        self.assertEqual(
            None,
            readable_date_text(object, 'invalid date'))

    def test_date_and_time_in_format_d_m_y_h_m(self):
        self.assertEqual(
            '17.10.2012 20:08',
            readable_date_time(object, datetime(2012, 10, 17, 20, 8)))

    def test_date_date_text_if_date_is_before_1900(self):
        self.assertEqual(
            None,
            readable_date_time(object, datetime(1000, 1, 1, 0, 0)))


class TestReadableDateTimeText(TestCase):

    def test_none_if_no_value_is_given(self):
        self.assertEqual(
            None,
            readable_date_time_text(object, None))

    def test_none_if_value_is_invalid(self):
        self.assertEqual(
            None,
            readable_date_time_text(object, 'invalid date'))

    def test_if_date_is_today_return_it_as_string(self):
        time_today = time(21, 8)
        self.assertEqual(
            'heute, 21:08',
            readable_date_time_text(
                object,
                datetime.combine(datetime.now(), time_today)))

    def test_if_date_is_yesterday_return_it_as_string(self):
        date_yesterday = (datetime.now() - timedelta(1)).date()
        time_yesterday = time(20, 8)
        self.assertEqual(
            'gestern, 20:08',
            readable_date_time_text(
                object,
                datetime.combine(date_yesterday, time_yesterday)))

    def test_if_date_is_older_than_yesterday_return_it_as_date(self):
        self.assertEqual(
            '17.10.2012 20:08',
            readable_date_time_text(object, datetime(2012, 10, 17, 20, 8)))


class TestReadableDateText(TestCase):

    def test_none_if_no_value_is_given(self):
        self.assertEqual(
            None,
            readable_date_text(object, None))

    def test_none_if_value_is_invalid(self):
        self.assertEqual(
            None,
            readable_date_text(object, 'invalid date'))

    def test_if_date_is_today_return_it_as_string(self):
        self.assertEqual(
            'heute',
            readable_date_text(object, datetime.now()))

    def test_if_date_is_yesterday_return_it_as_string(self):
        yesterday = (datetime.now() - timedelta(1))
        self.assertEqual(
            'gestern',
            readable_date_text(object, yesterday))

    def test_if_date_is_older_than_yesterday_return_it_as_date(self):
        self.assertEqual(
            '17.10.2012',
            readable_date_text(object, datetime(2012, 10, 17, 20, 8)))
