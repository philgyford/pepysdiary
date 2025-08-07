import time_machine
from django.utils.feedgenerator import rfc2822_date

from pepysdiary.common.utilities import make_datetime
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
from tests import FeedTestCase


class LatestArticlesFeedTestCase(FeedTestCase):
    def test_rss_element(self):
        "Testing the root <rss> element"
        feed = self.get_feed_element("/indepth/rss/")
        self.assertEqual(feed.getAttribute("version"), "2.0")

    def test_channel_element(self):
        "Testing the <channel> element and its contents (but not <item> contents)"

        # Need one Article so we have the most recent date for lastBuildDate.
        PublishedArticleFactory(
            title="Article 1", date_published=make_datetime("2021-04-07 12:00:00")
        )

        channel = self.get_channel_element("/indepth/rss/")

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
                "title": "The Diary of Samuel Pepys - In-Depth Articles",
                "description": "Articles about Samuel Pepys and his world",
                "link": "http://example.com/",
                "language": "en-gb",
                "lastBuildDate": rfc2822_date(make_datetime("2021-04-07 12:00:00")),
            },
        )

        # Check feed_url is passed
        self.assertEqual(
            channel.getElementsByTagName("atom:link")[0].getAttribute("href"),
            "http://example.com/indepth/rss/",
        )

    @time_machine.travel("2021-04-07 12:00:00 +0000", tick=False)
    def test_items(self):
        "Test the <item>s"

        articles = []
        for d in range(1, 4):
            article = PublishedArticleFactory(
                title=f"Article {d}",
                slug=f"article-{d}",
                intro=f"Intro {d}",
                text="",
                date_published=make_datetime(f"2021-04-07 12:00:0{d}"),
            )
            article.save()
            articles.append(article)

        channel = self.get_channel_element("/indepth/rss/")

        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 2)

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
                "title": "Article 3",
                "link": f"http://example.com/indepth/2021/04/07/{articles[2].slug}/",
                "description": "Intro 3",
                "dc:creator": "Phil Gyford",
                "pubDate": rfc2822_date(make_datetime("2021-04-07 12:00:03")),
                "guid": f"http://example.com/indepth/2021/04/07/{articles[2].slug}/",
                "content:encoded": (
                    "<p>Intro 3</p> "
                    "<p><strong>"
                    '<a href="http://example.com/indepth/2021/04/07/'
                    f"{articles[2].slug}/"
                    '#comments">Read the comments</a></strong></p>'
                ),
            },
        )

    def test_item_with_text(self):
        "Test that an item with text uses that"
        PublishedArticleFactory(
            title="Article 1",
            slug="article-1",
            intro="Intro 1",
            text="Text 1",
            date_published=make_datetime("2021-04-07 12:00:01"),
        )

        channel = self.get_channel_element("/indepth/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "content:encoded": (
                    "<p>Intro 1</p> "
                    "<p>Text 1</p> "
                    "<p><strong>"
                    '<a href="http://example.com/indepth/2021/04/07/article-1/'
                    '#comments">Read the comments</a></strong></p>'
                )
            },
        )

    def test_it_only_includes_published_articles(self):
        PublishedArticleFactory(
            title="Published Article",
            slug="published",
            intro="Intro",
            text="",
            date_published=make_datetime("2021-04-07 12:00:01"),
        )
        DraftArticleFactory(
            title="Draft Article",
            slug="draft",
            intro="Intro",
            text="",
            date_published=make_datetime("2021-04-07 12:00:02"),
        )

        channel = self.get_channel_element("/indepth/rss/")

        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 1)

        self.assertChildNodeContent(items[0], {"title": "Published Article"})
