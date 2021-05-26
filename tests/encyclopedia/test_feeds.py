from django.utils.feedgenerator import rfc2822_date
from freezegun import freeze_time

from pepysdiary.common.utilities import make_datetime
from pepysdiary.encyclopedia.factories import TopicFactory
from tests import FeedTestCase


class LatestTopicsFeedTestCase(FeedTestCase):
    def test_rss_element(self):
        "Testing the root <rss> element"
        feed = self.get_feed_element("/encyclopedia/rss/")
        self.assertEqual(feed.getAttribute("version"), "2.0")

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    def test_channel_element(self):
        "Testing the <channel> element and its contents (but not <item> contents)"

        # Need one topic so we have the most recent date for lastBuildDate.
        TopicFactory(title="Topic 1")

        channel = self.get_channel_element("/encyclopedia/rss/")

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
                "title": "Pepys' Diary - Encyclopedia Topics",
                "description": "New topics about Samuel Pepys and his world",
                "link": "http://example.com/",
                "language": "en-gb",
                "lastBuildDate": rfc2822_date(make_datetime("2021-04-07 12:00:00")),
            },
        )

        # Check feed_url is passed
        self.assertEqual(
            channel.getElementsByTagName("atom:link")[0].getAttribute("href"),
            "http://example.com/encyclopedia/rss/",
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    def test_items(self):
        "Test the <item>s"

        topics = []
        for d in range(1, 10):
            topic = TopicFactory(
                title=f"Topic {d}",
                summary=f"Summary {d}",
                wheatley="",
                tooltip_text="",
            )
            topic.date_created = make_datetime(f"2021-04-07 12:00:0{d}")
            topic.save()
            topics.append(topic)

        channel = self.get_channel_element("/encyclopedia/rss/")

        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 8)

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
                "title": "Topic 9",
                "link": f"http://example.com/encyclopedia/{topics[8].pk}/",
                "description": "Summary 9",
                "dc:creator": "Phil Gyford",
                "pubDate": rfc2822_date(make_datetime("2021-04-07 12:00:09")),
                "guid": f"http://example.com/encyclopedia/{topics[8].pk}/",
                "content:encoded": (
                    "<p>Summary 9</p> "
                    "<p><strong>"
                    f'<a href="http://example.com/encyclopedia/{topics[8].pk}/'
                    '#annotations">Read the annotations</a></strong></p>'
                ),
            },
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    def test_item_with_wheatley(self):
        "Test that an item with wheatley text uses that."

        topic = TopicFactory(
            title="Topic 1",
            summary="",
            wheatley="Wheatley text.",
            tooltip_text="",
        )

        channel = self.get_channel_element("/encyclopedia/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p>Wheatley text.</p> "
                    "<p><strong>"
                    f'<a href="http://example.com/encyclopedia/{topic.pk}/'
                    '#annotations">Read the annotations</a></strong></p>'
                ),
            },
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    def test_item_with_tooltip_text(self):
        "Test that an item with tooltip_text uses that."

        topic = TopicFactory(
            title="Topic 1",
            summary="",
            wheatley="",
            tooltip_text="Tooltip text.",
        )

        channel = self.get_channel_element("/encyclopedia/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p>Tooltip text.</p> "
                    "<p><strong>"
                    f'<a href="http://example.com/encyclopedia/{topic.pk}/'
                    '#annotations">Read the annotations</a></strong></p>'
                ),
            },
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    def test_item_with_no_texts(self):
        "Test that an item with no text fields uses an empty string."

        topic = TopicFactory(
            title="Topic 1",
            summary="",
            wheatley="",
            tooltip_text="",
        )

        channel = self.get_channel_element("/encyclopedia/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p><strong>"
                    f'<a href="http://example.com/encyclopedia/{topic.pk}/'
                    '#annotations">Read the annotations</a></strong></p>'
                ),
            },
        )
