from django.test import override_settings, TestCase
from freezegun import freeze_time

from pepysdiary.common.utilities import make_date
from pepysdiary.diary.models import Entry


class EntryManagerTestCase(TestCase):
    @freeze_time("2021-02-01 22:59:59", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_most_recent_entry_date_before_11pm_GMT(self):
        "Before 11pm, should return yesterday's date, in winter"
        d = Entry.objects.most_recent_entry_date()
        self.assertEqual(d, make_date("1668-01-31"))

    @freeze_time("2021-02-01 23:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_most_recent_entry_date_after_11pm_GMT(self):
        "From 11pm, should return today's date, in winter"
        d = Entry.objects.most_recent_entry_date()
        self.assertEqual(d, make_date("1668-02-01"))

    @freeze_time("2021-04-01 22:59:59", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_most_recent_entry_date_before_11pm_BST(self):
        "Before 11pm, should return yesterday's date, in summertime"
        d = Entry.objects.most_recent_entry_date()
        self.assertEqual(d, make_date("1668-03-31"))

    @freeze_time("2021-04-01 23:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_most_recent_entry_date_after_11pm_BST(self):
        "From 11pm, should return today's date, in summertime"
        d = Entry.objects.most_recent_entry_date()
        self.assertEqual(d, make_date("1668-04-01"))

    @freeze_time("2020-02-29 23:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_most_recent_entry_date_leap_year(self):
        "If now is Feb 29th but entry date isn't a leap year, should return 28th"
        d = Entry.objects.most_recent_entry_date()
        self.assertEqual(d, make_date("1667-02-28"))

    def test_all_years_months_invalid_format(self):
        with self.assertRaises(ValueError):
            Entry.objects.all_years_months(month_format="c")

    def test_all_years_months_format_default(self):
        "It should return the correct data with default args"
        data = Entry.objects.all_years_months()
        self.assertEqual(len(data), 10)
        self.assertEqual(data[9], ("1669", ("Jan", "Feb", "Mar", "Apr", "May")))

    def test_all_years_months_format_b(self):
        "It should return the correct data with month_format='b'"
        data = Entry.objects.all_years_months(month_format="b")
        self.assertEqual(len(data), 10)
        self.assertEqual(data[9], ("1669", ("Jan", "Feb", "Mar", "Apr", "May")))

    def test_all_years_months_format_m(self):
        "It should return the correct data with month_format='m'"
        data = Entry.objects.all_years_months(month_format="m")
        self.assertEqual(len(data), 10)
        self.assertEqual(data[9], ("1669", ("01", "02", "03", "04", "05")))

    def test_all_years(self):
        "It should return the correct data"
        self.assertEqual(
            Entry.objects.all_years(),
            [
                "1660",
                "1661",
                "1662",
                "1663",
                "1664",
                "1665",
                "1666",
                "1667",
                "1668",
                "1669",
            ],
        )
