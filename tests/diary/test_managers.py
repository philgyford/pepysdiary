from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from freezegun import freeze_time

from pepysdiary.common.utilities import make_date
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.factories import TopicFactory


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

    def test_get_brief_references(self):
        "It should return the correct data about topics referenced by Entry texts"

        topic_1 = TopicFactory(
            title="Cats",
            tooltip_text="About cats",
            thumbnail=SimpleUploadedFile(
                name="cat.jpg", content=b"", content_type="image/jpeg"
            ),
        )
        topic_2 = TopicFactory(title="Dogs", tooltip_text="About dogs")
        topic_3 = TopicFactory(title="Fish", tooltip_text="About fish")
        TopicFactory(title="Birds")

        entry_1 = EntryFactory(
            text=(
                "<p>"
                f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
                "</a> and "
                f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_3.id}/">fish'
                "</a>.</p>"
            )
        )
        entry_2 = EntryFactory(
            text=(
                "<p>"
                f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
                "</a> and "
                f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_2.id}/">dogs'
                "</a>.</p>"
            )
        )

        references = Entry.objects.get_brief_references([entry_1, entry_2])

        self.assertEqual(len(references.keys()), 3)
        self.assertEqual(
            references[str(topic_1.pk)],
            {
                "title": "Cats",
                "text": "About cats",
                "thumbnail_url": "/media/encyclopedia/thumbnails/cat.jpg",
            },
        )
        self.assertEqual(
            references[str(topic_3.pk)],
            {"title": "Fish", "text": "About fish", "thumbnail_url": ""},
        )
        self.assertEqual(
            references[str(topic_2.pk)],
            {"title": "Dogs", "text": "About dogs", "thumbnail_url": ""},
        )

        # Tidy up the file
        topic_1.thumbnail.delete()
