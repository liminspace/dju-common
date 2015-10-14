import datetime
from django.test import TestCase
from django.utils import timezone
import pytz
from dju_common.tools import datetime_to_dtstr, dtstr_to_datetime, int2base36


class TestTools(TestCase):
    def test_datetime_to_dtstr_to_datetime(self):
        dt = datetime.datetime(2015, 11, 9, 22, 15, 45, 125000)
        dtstr = datetime_to_dtstr(dt)
        self.assertEqual(dtstr, 'igsiclph')
        self.assertEqual(dtstr_to_datetime(dtstr), dt)

        dt = datetime.datetime(2015, 7, 9, 22, 15, 45, 125000)
        dtstr = datetime_to_dtstr(dt)
        self.assertEqual(dtstr, 'ibwr6tph')
        self.assertEqual(dtstr_to_datetime(dtstr), dt)

    def test_datetime_to_dtstr_to_datetime_for_aware(self):
        dt1 = timezone.make_aware(datetime.datetime(2015, 11, 9, 22, 15, 45, 125000), pytz.timezone('Europe/Kiev'))
        dtstr = datetime_to_dtstr(dt1)
        self.assertEqual(dtstr, 'igse2a5h')
        dt2 = timezone.make_aware(dtstr_to_datetime(dtstr), pytz.UTC).astimezone(pytz.timezone('Europe/Kiev'))
        self.assertEqual(dt2, dt1)

        dt1 = timezone.make_aware(datetime.datetime(2015, 7, 9, 22, 15, 45, 125000), pytz.timezone('Europe/Kiev'))
        dtstr = datetime_to_dtstr(dt1)
        self.assertEqual(dtstr, 'ibwkrcdh')
        dt2 = timezone.make_aware(dtstr_to_datetime(dtstr), pytz.UTC).astimezone(pytz.timezone('Europe/Kiev'))
        self.assertEqual(dt2, dt1)

    def test_datetime_to_dtstr_to_datetime_with_tz(self):
        dt = timezone.make_aware(datetime.datetime(2015, 11, 9, 22, 15, 45, 125000), pytz.timezone('Europe/Kiev'))
        dtstr = datetime_to_dtstr(dt)
        self.assertEqual(dtstr, 'igse2a5h')
        self.assertEqual(dtstr_to_datetime(dtstr, to_tz=pytz.timezone('Europe/Kiev')), dt)

        dt = timezone.make_aware(datetime.datetime(2015, 7, 9, 22, 15, 45, 125000), pytz.timezone('Europe/Kiev'))
        dtstr = datetime_to_dtstr(dt)
        self.assertEqual(dtstr, 'ibwkrcdh')
        self.assertEqual(dtstr_to_datetime(dtstr, to_tz=pytz.timezone('Europe/Kiev')), dt)

    def test_datetime_to_dtstr_without_dt(self):
        now = datetime.datetime.utcnow()
        now = now.replace(microsecond=int(int(now.microsecond / 1e3) * 1e3))  # because 1s = 1000ms in timestamp
        dtstr = datetime_to_dtstr()
        self.assertTrue(now <= dtstr_to_datetime(dtstr) < now + datetime.timedelta(seconds=5))

    def test_dtstr_to_datetime_with_error(self):
        self.assertIsNone(dtstr_to_datetime('abcdefg!'))
        with self.assertRaises(ValueError):
            dtstr_to_datetime('abcdefg!', fail_silently=False)

    def test_int2base36(self):
        self.assertEqual(int2base36(30), 'u')
        self.assertEqual(int2base36(-30), '-u')
        self.assertEqual(int2base36(159), '4f')
        self.assertEqual(int2base36(-159), '-4f')
        self.assertEqual(int(int2base36(159159159), 36), 159159159)
        self.assertEqual(int(int2base36(-159159159), 36), -159159159)
