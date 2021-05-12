from django.test import override_settings, TestCase

from django_comments.moderation import CommentModerator

from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.diary.factories import EntryFactory, SummaryFactory
from pepysdiary.diary.models import Entry, EntryModerator, Summary
from pepysdiary.encyclopedia.factories import TopicFactory


class EntryTestCase(TestCase):
    def test_ordering(self):
        "The default manager should order objects by diary_date ascending"
        entry_2 = EntryFactory(diary_date=make_date("1660-01-02"))
        entry_3 = EntryFactory(diary_date=make_date("1660-01-03"))
        entry_1 = EntryFactory(diary_date=make_date("1660-01-01"))

        entries = Entry.objects.all()

        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0], entry_1)
        self.assertEqual(entries[1], entry_2)
        self.assertEqual(entries[2], entry_3)

    def test_str(self):
        "The string representation should be the title"
        title = "Monday 24 February 1667/68"
        entry = EntryFactory(title=title)
        self.assertEqual(str(entry), title)

    def test_makes_references_on_save(self):
        "When an Entry is saved, any references should be updated."
        topic_1 = TopicFactory(title="Cats")
        topic_2 = TopicFactory(title="Dogs")
        topic_3 = TopicFactory(title="Fish")
        entry = EntryFactory(text="")

        # Manually add the entry as a reference only to topics 1 and 2:
        topic_1.diary_references.add(entry)
        topic_2.diary_references.add(entry)

        # Now save the entry with text referencing only topics 1 and 3:
        # This should update the references.
        entry.text = (
            "<p>Hello. "
            f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
            "</a> and "
            f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_3.id}/">fish'
            "</a>.</p>"
        )
        entry.save()

        # Should still be there:
        topic_1_refs = topic_1.diary_references.all()
        self.assertEqual(len(topic_1_refs), 1)
        self.assertEqual(topic_1_refs[0], entry)

        # Should no longer exist:
        topic_2_refs = topic_2.diary_references.all()
        self.assertEqual(len(topic_2_refs), 0)

        # Should have been added:
        topic_3_refs = topic_3.diary_references.all()
        self.assertEqual(len(topic_3_refs), 1)
        self.assertEqual(topic_3_refs[0], entry)

    def test_get_absolute_url(self):
        "It should return the correct URL"
        entry = EntryFactory(diary_date=make_date("1660-01-01"))
        self.assertEqual(entry.get_absolute_url(), "/diary/1660/01/01/")

    def test_index_components(self):
        "It should return the correct value"
        entry = EntryFactory(title="Title", text="Text", footnotes="Footnotes")
        self.assertEqual(
            entry.index_components(),
            (("Title", "A"), ("Text", "B"), ("Footnotes", "C")),
        )

    @override_settings(YEARS_OFFSET=350)
    def test_date_published(self):
        "It should return the correct modern datetime"
        entry = EntryFactory(diary_date=make_date("1660-01-01"))
        self.assertEqual(entry.date_published, make_datetime("2010-01-01 23:00:00"))

    @override_settings(YEARS_OFFSET=350)
    def test_date_published_29_feb(self):
        "If 17th C date is 29 feb, but there's none in modern day, should be 1st March"
        entry = EntryFactory(diary_date=make_date("1668-02-29"))
        self.assertEqual(entry.date_published, make_datetime("2018-03-01 23:00:00"))

    def test_short_title(self):
        "It should return the correct short title"
        # Just test a couple.

        entry = EntryFactory(
            title="Monday 16 September 1661", diary_date=make_date("1661-09-16")
        )
        self.assertEqual(entry.short_title, "Mon 16 Sep 1661")

        entry = EntryFactory(
            title="Saturday 29 February 1667/68", diary_date=make_date("1668-02-29")
        )
        self.assertEqual(entry.short_title, "Sat 29 Feb 1667/68")


def EntryModeratorTestCase(TestCase):
    def test_properties(self):
        "Just testing it exists I guess?"
        em = EntryModerator()
        self.assertTrue(issubclass(em, CommentModerator))
        self.assertFalse(em.email_notifications)
        self.essetEqual(em.enable_field, "allow_comments")


class SummaryTestCase(TestCase):
    def test_ordering(self):
        "Summaries should be ordered by summary_date"
        summary_2 = SummaryFactory(summary_date=make_date("1660-01-02"))
        summary_3 = SummaryFactory(summary_date=make_date("1660-01-03"))
        summary_1 = SummaryFactory(summary_date=make_date("1660-01-01"))

        summaries = Summary.objects.all()

        self.assertEqual(len(summaries), 3)
        self.assertEqual(summaries[0], summary_1)
        self.assertEqual(summaries[1], summary_2)
        self.assertEqual(summaries[2], summary_3)

    def test_str(self):
        "The str representatino should use the title"
        summary = SummaryFactory(title="January 1667/68")
        self.assertEqual(str(summary), "January 1667/68")

    def test_text_html_set_on_save(self):
        "It should save a markdown version of text in text_html on save"
        summary = SummaryFactory(text="This is **my** [test](http://example.org).")
        self.assertEqual(
            summary.text_html,
            '<p>This is <strong>my</strong> <a href="http://example.org">test</a>.</p>',
        )
