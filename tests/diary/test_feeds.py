from django.test import override_settings
from django.utils.feedgenerator import rfc2822_date
from freezegun import freeze_time

from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.diary.factories import EntryFactory
from tests import FeedTestCase


class LatestEntriesFeedTestCase(FeedTestCase):
    def test_rss_element(self):
        "Testing the root <rss> element"
        feed = self.get_feed_element("/diary/rss/")
        self.assertEqual(feed.getAttribute("version"), "2.0")

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_channel_element(self):
        "Testing the <channel> element and its contents (but not <item> contents)"

        # Need one entry so we have the most recent date for lastBuildDate.
        EntryFactory(title="Entry 6", diary_date=make_date("1668-04-06"))

        channel = self.get_channel_element("/diary/rss/")

        self.assertChildNodes(
            channel,
            [
                "title",
                "link",
                "description",
                "atom:link",
                "language",
                "lastBuildDate",
                "item",
            ],
        )
        self.assertChildNodeContent(
            channel,
            {
                "title": "The Diary of Samuel Pepys",
                "description": "Daily entries from the 17th century London diary",
                "link": "http://example.com/",
                "language": "en-gb",
                "lastBuildDate": rfc2822_date(make_datetime("2021-04-06 23:00:00")),
            },
        )

        # Check feed_url is passed
        self.assertEqual(
            channel.getElementsByTagName("atom:link")[0].getAttribute("href"),
            "http://example.com/diary/rss/",
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_items(self):
        "Test the <item>s"

        for d in range(1, 7):
            EntryFactory(
                title=f"Entry {d}",
                diary_date=make_date(f"1668-04-0{d}"),
                text=f"<p>Description {d}</p>",
            )

        # 1 unpublished entry:
        EntryFactory(diary_date=make_date("1668-04-07"))

        channel = self.get_channel_element("/diary/rss/")

        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 5)

        for item in items:
            self.assertChildNodes(
                item,
                [
                    "title",
                    "link",
                    "description",
                    "dc:creator",
                    "pubDate",
                    "guid",
                    "content:encoded",
                ],
            )

        # Check the contents of the first item.
        self.assertChildNodeContent(
            items[0],
            {
                "title": "Entry 6",
                "link": "http://example.com/diary/1668/04/06/",
                "description": "Description 6",
                "dc:creator": "Samuel Pepys",
                "pubDate": rfc2822_date(make_datetime("2021-04-06 23:00:00")),
                "guid": "http://example.com/diary/1668/04/06/",
                "content:encoded": (
                    "<p>Description 6</p> "
                    "<p><strong>"
                    '<a href="http://example.com/diary/1668/04/06/#annotations">'
                    "Read the annotations</a>"
                    "</strong></p>"
                ),
            },
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_item_with_footnotes(self):
        "Test that an item with footnotes has them included."
        EntryFactory(
            title="Entry 6",
            diary_date=make_date("1668-04-06"),
            text="<p>Description 6</p>",
            footnotes="<ol><li>Footnote 6</li></ol>",
        )

        channel = self.get_channel_element("/diary/rss/")

        items = channel.getElementsByTagName("item")

        # self.maxDiff = None
        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p>Description 6</p> "
                    "<p><strong>Footnotes</strong></p>"
                    "<aside><ol><li>Footnote 6</li></ol>"
                    "</aside> "
                    "<p><strong>"
                    '<a href="http://example.com/diary/1668/04/06/#annotations">'
                    "Read the annotations</a>"
                    "</strong></p>"
                )
            },
        )
