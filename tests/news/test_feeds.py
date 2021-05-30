from django.utils.feedgenerator import rfc2822_date
from freezegun import freeze_time

from pepysdiary.common.utilities import make_datetime
from pepysdiary.news.factories import DraftPostFactory, PublishedPostFactory
from tests import FeedTestCase


class LatestPostsFeedTestCase(FeedTestCase):
    def test_rss_element(self):
        "Testing the root <rss> element"
        feed = self.get_feed_element("/news/rss/")
        self.assertEqual(feed.getAttribute("version"), "2.0")

    def test_channel_element(self):
        "Testing the <channel> element and its contents (but not <item> contents)"

        # Need one Post so we have the most recent date for lastBuildDate.
        PublishedPostFactory(
            title="Post 1", date_published=make_datetime("2021-04-07 12:00:00")
        )

        channel = self.get_channel_element("/news/rss/")

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
                "title": "The Diary of Samuel Pepys - Site News",
                "description": "News about the Diary of Samuel Pepys website",
                "link": "http://example.com/",
                "language": "en-gb",
                "lastBuildDate": rfc2822_date(make_datetime("2021-04-07 12:00:00")),
            },
        )

        # Check feed_url is passed
        self.assertEqual(
            channel.getElementsByTagName("atom:link")[0].getAttribute("href"),
            "http://example.com/news/rss/",
        )

    @freeze_time("2021-04-07 12:00:00", tz_offset=0)
    def test_items(self):
        "Test the <item>s"

        posts = []
        for d in range(1, 5):
            post = PublishedPostFactory(
                title=f"Post {d}",
                intro=f"Intro {d}",
                text="",
                date_published=make_datetime(f"2021-04-07 12:00:0{d}"),
            )
            post.save()
            posts.append(post)

        channel = self.get_channel_element("/news/rss/")

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
                "title": "Post 4",
                "link": f"http://example.com/news/2021/04/07/{posts[3].pk}/",
                "description": "Intro 4",
                "dc:creator": "Phil Gyford",
                "pubDate": rfc2822_date(make_datetime("2021-04-07 12:00:04")),
                "guid": f"http://example.com/news/2021/04/07/{posts[3].pk}/",
                "content:encoded": (
                    "<p>Intro 4</p> "
                    "<p><strong>"
                    '<a href="http://example.com/news/2021/04/07/'
                    f"{posts[3].pk}/"
                    '#comments">Read the comments</a></strong></p>'
                ),
            },
        )

    def test_item_with_text(self):
        "Test that an item with text uses that"
        post = PublishedPostFactory(
            title="Post 1",
            intro="Intro 1",
            text="Text 1",
            date_published=make_datetime("2021-04-07 12:00:01"),
        )

        channel = self.get_channel_element("/news/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p>Intro 1</p> "
                    "<p>Text 1</p> "
                    "<p><strong>"
                    f'<a href="http://example.com/news/2021/04/07/{post.pk}/'
                    '#comments">Read the comments</a></strong></p>'
                )
            },
        )

    def test_it_only_includes_published_articles(self):
        PublishedPostFactory(
            title="Published Post",
            intro="Intro",
            text="",
            date_published=make_datetime("2021-04-07 12:00:01"),
        )
        DraftPostFactory(
            title="Draft Post",
            intro="Intro",
            text="",
            date_published=make_datetime("2021-04-07 12:00:02"),
        )

        channel = self.get_channel_element("/news/rss/")

        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 1)

        self.assertChildNodeContent(items[0], {"title": "Published Post"})
