from django.test import TestCase, override_settings
from django_comments.moderation import AlreadyModerated, moderator

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

    def test_makes_references_invalid_link(self):
        "If a link looks like a reference but is invalid, should be ignored"
        topic_1 = TopicFactory(title="Cats")
        entry = EntryFactory(text="")

        entry.text = (
            "<p>Hello. "
            f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
            "</a> and "
            f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_1.id}999999/">broken'
            "</a>.</p>"
        )
        entry.save()

        # The 1 valid link should have created a reference:
        topic_1_refs = topic_1.diary_references.all()
        self.assertEqual(len(topic_1_refs), 1)
        self.assertEqual(topic_1_refs[0], entry)

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

    # Testing PepysModel properties/methods:

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

    def test_text_for_rss(self):
        "It should remove the links to footnotes, leaving other links as is"
        text = """<p>Blessed be God <sup id="fnr1-1660-01-01"><a href="#fn1-1660-01-01">1</a></sup></p>

<p>I lived in <a href="http://www.pepysdiary.com/foo/">Axe Yard</a> having <sup id="fnr2-1660-01-01"><a href="#fn2-1660-01-01">2</a></sup> The condition of the State was thus</p>"""  # noqa: E501

        entry = EntryFactory(text=text)
        self.assertHTMLEqual(
            entry.text_for_rss,
            """<p>Blessed be God <sup id="fnr1-1660-01-01">1</sup></p>

<p>I lived in <a href="http://www.pepysdiary.com/foo/">Axe Yard</a> having <sup id="fnr2-1660-01-01">2</sup> The condition of the State was thus</p>""",  # noqa: E501
        )

    def test_footnotes_for_rss(self):
        "It should remove the return links from footnotes, leaving other links as is"
        footnotes = """<ol>
<li id="fn1-1660-01-01">Pepys was successfully cut for <a href="http://www.pepysdiary.com/foo/">the stone</a> on. <a href="#fnr1-1660-01-01">&#8617;</a></li>

<li id="fn2-1660-01-01">This is the first. <a href="#fnr2-1660-01-01">&#8617;</a></li>
</ol>
"""  # noqa: E501

        entry = EntryFactory(footnotes=footnotes)
        self.assertHTMLEqual(
            entry.footnotes_for_rss,
            """<aside>
<ol>
<li id="fn1-1660-01-01">Pepys was successfully cut for <a href="http://www.pepysdiary.com/foo/">the stone</a> on. </li>

<li id="fn2-1660-01-01">This is the first. </li>
</ol>
</aside>
""",  # noqa: E501
        )

    def test_get_a_comment_name(self):
        "It should retun the correct string"
        entry = EntryFactory()
        self.assertEqual(entry.get_a_comment_name(), "an annotation")

    # Testing OldDateMixin properties/methods:

    def test_old_dates(self):
        "The properties should return the correct data"
        entry = EntryFactory(diary_date=make_date("1660-01-02"))
        self.assertEqual(entry.year, "1660")
        self.assertEqual(entry.month, "01")
        self.assertEqual(entry.month_b, "Jan")
        self.assertEqual(entry.day, "02")
        self.assertEqual(entry.day_e, "2")


class EntryModeratorTestCase(TestCase):
    def test_it_is_registered(self):
        # Shouldn't be able to register it again:
        with self.assertRaises(AlreadyModerated):
            moderator.register(Entry, EntryModerator)


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

    # Testing PepysModel properties/methods:

    def test_short_title(self):
        "It should return the correct short title"
        # Just test a couple.

        summary = SummaryFactory(
            title="September 1661", summary_date=make_date("1661-09-01")
        )
        self.assertEqual(summary.short_title, "September 1661")

    def test_get_a_comment_name(self):
        "It should retun the correct string"
        summary = SummaryFactory()
        self.assertEqual(summary.get_a_comment_name(), "a comment")

    # Testing OldDateMixin properties/methods:

    def test_old_dates(self):
        "The properties should return the correct data"
        summary = SummaryFactory(summary_date=make_date("1660-01-02"))
        self.assertEqual(summary.year, "1660")
        self.assertEqual(summary.month, "01")
        self.assertEqual(summary.month_b, "Jan")
        self.assertEqual(summary.day, "02")
        self.assertEqual(summary.day_e, "2")
