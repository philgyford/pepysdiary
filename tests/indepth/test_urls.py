from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.indepth import feeds
from pepysdiary.indepth import views


class InDepthURLsTestCase(TestCase):
    """Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_article_rss_url(self):
        self.assertEqual(reverse("article_rss"), "/indepth/rss/")

    def test_article_rss_view(self):
        self.assertEqual(
            resolve("/indepth/rss/").func.__class__.__name__,
            feeds.LatestArticlesFeed.__name__,
        )

    def test_article_detail_url(self):
        self.assertEqual(
            reverse(
                "article_detail",
                kwargs={
                    "year": "2021",
                    "month": "01",
                    "day": "02",
                    "slug": "my-article",
                },
            ),
            "/indepth/2021/01/02/my-article/",
        )

    def test_article_detail_view(self):
        self.assertEqual(
            resolve("/indepth/2021/01/02/my-article/").func.__name__,
            views.ArticleDetailView.__name__,
        )

    def test_article_archive_url(self):
        self.assertEqual(reverse("indepth"), "/indepth/")

    def test_article_archive_view(self):
        self.assertEqual(
            resolve("/indepth/").func.__name__, views.ArticleArchiveView.__name__
        )
