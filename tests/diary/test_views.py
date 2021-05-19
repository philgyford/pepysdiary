from django.http.response import Http404

from pepysdiary.common.utilities import make_date
from pepysdiary.diary import views
from pepysdiary.diary.factories import EntryFactory, SummaryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from tests import ViewTestCase


class EntryDetailViewTestCase(ViewTestCase):
    def test_response_200(self):
        "If the Entry exists, it returns 200"
        EntryFactory(diary_date=make_date("1661-01-02"))
        response = views.EntryDetailView.as_view()(
            self.request, year="1661", month="01", day="02"
        )
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        EntryFactory(diary_date=make_date("1661-01-02"))
        response = views.EntryDetailView.as_view()(
            self.request, year="1661", month="01", day="02"
        )
        self.assertEqual(response.template_name[0], "diary/entry_detail.html")

    def test_response_404_no_entry(self):
        "It 404s if there's no Entry for this date"
        with self.assertRaises(Http404):
            views.EntryDetailView.as_view()(
                self.request, year="1661", month="01", day="02"
            )

    def test_context_data_tooltip_references(self):
        "The tooltip_references are sent to the template"
        entry = EntryFactory(diary_date=make_date("1661-01-02"))
        topic_1 = TopicFactory(title="Cats", tooltip_text="About cats")
        topic_2 = TopicFactory(title="Dogs", tooltip_text="About dogs")
        topic_1.diary_references.add(entry)
        topic_2.diary_references.add(entry)

        response = views.EntryDetailView.as_view()(
            self.request, year="1661", month="01", day="02"
        )
        self.assertIn("tooltip_references", response.context_data)
        self.assertEqual(
            response.context_data["tooltip_references"],
            {
                str(topic_1.pk): {
                    "title": "Cats",
                    "text": "About cats",
                    "thumbnail_url": "",
                },
                str(topic_2.pk): {
                    "title": "Dogs",
                    "text": "About dogs",
                    "thumbnail_url": "",
                },
            },
        )

    def test_context_data_next_previous(self):
        "Next and previous entries are sent to the template when they exist"
        previous_entry = EntryFactory(diary_date=make_date("1661-01-01"))
        EntryFactory(diary_date=make_date("1661-01-02"))
        next_entry = EntryFactory(diary_date=make_date("1661-01-03"))

        response = views.EntryDetailView.as_view()(
            self.request, year="1661", month="01", day="02"
        )
        self.assertIn("previous_entry", response.context_data)
        self.assertEqual(response.context_data["previous_entry"], previous_entry)
        self.assertIn("next_entry", response.context_data)
        self.assertEqual(response.context_data["next_entry"], next_entry)

    def test_context_data_no_next_previous(self):
        "If there's no next and previous entries, None is sent to the template"
        EntryFactory(diary_date=make_date("1661-01-02"))

        response = views.EntryDetailView.as_view()(
            self.request, year="1661", month="01", day="02"
        )
        self.assertIn("previous_entry", response.context_data)
        self.assertIsNone(response.context_data["previous_entry"])
        self.assertIn("next_entry", response.context_data)
        self.assertIsNone(response.context_data["next_entry"])


class EntryMonthArchiveViewTestCase(ViewTestCase):
    def test_response_200(self):
        "If there are Entries for this month, it returns 200"
        EntryFactory(diary_date=make_date("1661-01-02"))
        response = views.EntryMonthArchiveView.as_view()(
            self.request, year="1661", month="01"
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404_no_entries(self):
        "It 404s if there are no Entries for this month"
        with self.assertRaises(Http404):
            views.EntryMonthArchiveView.as_view()(self.request, year="1661", month="01")

    def test_template(self):
        EntryFactory(diary_date=make_date("1661-01-02"))
        response = views.EntryMonthArchiveView.as_view()(
            self.request, year="1661", month="01"
        )
        self.assertEqual(response.template_name[0], "diary/entry_archive_month.html")

    def test_ordering(self):
        "Entries should be ordered by diary_date ascending"
        entry_1 = EntryFactory(diary_date=make_date("1661-01-02"))
        entry_2 = EntryFactory(diary_date=make_date("1661-01-03"))
        entry_3 = EntryFactory(diary_date=make_date("1661-01-01"))

        response = views.EntryMonthArchiveView.as_view()(
            self.request, year="1661", month="01"
        )
        entries = response.context_data["object_list"]
        self.assertEqual(entries[0], entry_3)
        self.assertEqual(entries[1], entry_1)
        self.assertEqual(entries[2], entry_2)

    def test_context_entries(self):
        "entry_list and object_list should exist in the context"
        entry = EntryFactory(diary_date=make_date("1661-01-02"))
        # Shouldn't be included:
        EntryFactory(diary_date=make_date("1661-02-01"))

        response = views.EntryMonthArchiveView.as_view()(
            self.request, year="1661", month="01"
        )
        self.assertIn("object_list", response.context_data)
        self.assertEqual(len(response.context_data["object_list"]), 1)
        self.assertEqual(response.context_data["object_list"][0], entry)

        self.assertIn("entry_list", response.context_data)
        self.assertEqual(
            response.context_data["object_list"], response.context_data["entry_list"]
        )

    def test_context_tooltip_references(self):
        "The correct tooltip references should be included in the context"

        topic_1 = TopicFactory(title="Cats", tooltip_text="About cats")
        topic_2 = TopicFactory(title="Dogs", tooltip_text="About dogs")
        topic_3 = TopicFactory(title="Fish", tooltip_text="About fish")

        entry_1 = EntryFactory(diary_date=make_date("1661-01-02"))
        topic_1.diary_references.add(entry_1)
        topic_2.diary_references.add(entry_1)

        entry_2 = EntryFactory(diary_date=make_date("1661-01-03"))
        topic_2.diary_references.add(entry_2)
        topic_3.diary_references.add(entry_2)

        response = views.EntryMonthArchiveView.as_view()(
            self.request, year="1661", month="01"
        )
        self.assertIn("tooltip_references", response.context_data)
        self.assertEqual(
            response.context_data["tooltip_references"],
            {
                str(topic_1.pk): {
                    "title": "Cats",
                    "text": "About cats",
                    "thumbnail_url": "",
                },
                str(topic_2.pk): {
                    "title": "Dogs",
                    "text": "About dogs",
                    "thumbnail_url": "",
                },
                str(topic_3.pk): {
                    "title": "Fish",
                    "text": "About fish",
                    "thumbnail_url": "",
                },
            },
        )


class EntryArchiveIndexViewTestCase(ViewTestCase):
    def test_response_200(self):
        EntryFactory(diary_date=make_date("1661-01-02"))
        response = views.EntryArchiveIndexView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should raise 404 if there are no Entries"
        with self.assertRaises(Http404):
            views.EntryArchiveIndexView.as_view()(self.request)

    def test_template(self):
        EntryFactory(diary_date=make_date("1661-01-02"))
        response = views.EntryArchiveIndexView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "diary/entry_archive.html")

    def test_context_date_list(self):
        "The date_list should contain the dates per month"
        EntryFactory(diary_date=make_date("1661-01-02"))
        EntryFactory(diary_date=make_date("1662-01-01"))
        EntryFactory(diary_date=make_date("1661-02-01"))

        response = views.EntryArchiveIndexView.as_view()(self.request)

        self.assertIn("date_list", response.context_data)
        dates = response.context_data["date_list"]
        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], make_date("1661-01-01"))
        self.assertEqual(dates[1], make_date("1661-02-01"))
        self.assertEqual(dates[2], make_date("1662-01-01"))

    def test_context_object_list(self):
        "The object_list should contain the Entries in reverse chronological order"
        entry_1 = EntryFactory(diary_date=make_date("1661-01-02"))
        entry_2 = EntryFactory(diary_date=make_date("1661-01-03"))
        entry_3 = EntryFactory(diary_date=make_date("1661-01-01"))

        response = views.EntryArchiveIndexView.as_view()(self.request)

        self.assertIn("object_list", response.context_data)
        entries = response.context_data["object_list"]
        self.assertEqual(entries[0], entry_2)
        self.assertEqual(entries[1], entry_1)
        self.assertEqual(entries[2], entry_3)


class SummaryYearArchiveView(ViewTestCase):
    def test_response_200(self):
        "If there are Summaries for this year, it returns 200"
        SummaryFactory(summary_date=make_date("1661-01-01"))
        response = views.SummaryYearArchiveView.as_view()(self.request, year="1661")
        self.assertEqual(response.status_code, 200)

    def test_response_404_no_entries(self):
        "It 404s if there are no Summaries for this year"
        with self.assertRaises(Http404):
            views.SummaryYearArchiveView.as_view()(self.request, year="1661")

    def test_template(self):
        SummaryFactory(summary_date=make_date("1661-01-01"))
        response = views.SummaryYearArchiveView.as_view()(self.request, year="1661")
        self.assertEqual(response.template_name[0], "diary/summary_archive_year.html")

    def test_context_summary_list(self):
        "It should include summary_list and object_list"
        summary_1 = SummaryFactory(summary_date=make_date("1661-02-01"))
        summary_2 = SummaryFactory(summary_date=make_date("1661-03-01"))
        summary_3 = SummaryFactory(summary_date=make_date("1661-01-01"))

        # Shouldn't be included:
        SummaryFactory(summary_date=make_date("1662-01-01"))

        response = views.SummaryYearArchiveView.as_view()(self.request, year="1661")

        self.assertIn("object_list", response.context_data)
        self.assertIn("summary_list", response.context_data)
        self.assertEqual(
            response.context_data["object_list"], response.context_data["summary_list"]
        )

        summaries = response.context_data["object_list"]
        self.assertEqual(len(summaries), 3)
        self.assertEqual(summaries[0], summary_2)
        self.assertEqual(summaries[1], summary_1)
        self.assertEqual(summaries[2], summary_3)
