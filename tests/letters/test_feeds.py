import time_machine
from django.utils.feedgenerator import rfc2822_date

from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.letters.factories import LetterFactory
from tests import FeedTestCase


class LatestLettersFeedTestCase(FeedTestCase):
    def test_rss_element(self):
        "Testing the root <rss> element"
        feed = self.get_feed_element("/letters/rss/")
        self.assertEqual(feed.getAttribute("version"), "2.0")

    @time_machine.travel("2021-04-07 12:00:00 +0000", tick=False)
    def test_channel_element(self):
        "Testing the <channel> element and its contents (but not <item> contents)"

        # Need one topic so we have the most recent date for lastBuildDate.
        LetterFactory(title="Topic 1")

        channel = self.get_channel_element("/letters/rss/")

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
                "title": "Pepys' Diary - Letters",
                "description": "Letters sent by or to Samuel Pepys",
                "link": "http://example.com/",
                "language": "en-gb",
                "lastBuildDate": rfc2822_date(make_datetime("2021-04-07 12:00:00")),
            },
        )

        # Check feed_url is passed
        self.assertEqual(
            channel.getElementsByTagName("atom:link")[0].getAttribute("href"),
            "http://example.com/letters/rss/",
        )

    @time_machine.travel("2021-04-07 12:00:00 +0000", tick=False)
    def test_items(self):
        "Test the <item>s"

        letters = []
        for d in range(1, 5):
            letter = LetterFactory(
                title=f"Letter {d}",
                text=f"<p>Text {d}</p>",
                footnotes="",
                slug=f"letter-{d}",
                letter_date=make_date("1660-01-02"),
            )
            letter.date_created = make_datetime(f"2021-04-07 12:00:0{d}")
            letter.save()
            letters.append(letter)

        channel = self.get_channel_element("/letters/rss/")

        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 3)

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
                "title": "Letter 4",
                "link": f"http://example.com/letters/1660/01/02/{letters[3].slug}/",
                "description": "Text 4",
                "dc:creator": "Phil Gyford",
                "pubDate": rfc2822_date(make_datetime("2021-04-07 12:00:04")),
                "guid": f"http://example.com/letters/1660/01/02/{letters[3].slug}/",
                "content:encoded": (
                    "<p>Text 4</p> "
                    "<p><strong>"
                    f'<a href="http://example.com/letters/1660/01/02/{letters[3].slug}/'
                    '#annotations">Read the annotations</a></strong></p>'
                ),
            },
        )

    @time_machine.travel("2021-04-07 12:00:00 +0000", tick=False)
    def test_item_with_footnotes(self):
        "Test that an item with footnotes shows that."

        LetterFactory(
            title="Letter 1",
            text="<p>Text 1</p>",
            footnotes="<p>Footnotes 1</p>",
            slug="letter-1",
            letter_date=make_date("1660-01-02"),
        )

        channel = self.get_channel_element("/letters/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p>Text 1</p> "
                    "<p>Footnotes 1</p> "
                    "<p><strong>"
                    '<a href="http://example.com/letters/1660/01/02/letter-1/'
                    '#annotations">Read the annotations</a></strong></p>'
                ),
            },
        )
