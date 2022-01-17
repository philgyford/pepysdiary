from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.news import feeds
from pepysdiary.news import views


class NewsURLsTestCase(TestCase):
    """Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_post_rss_url(self):
        self.assertEqual(reverse("post_rss"), "/news/rss/")

    def test_post_rss_view(self):
        self.assertEqual(
            resolve("/news/rss/").func.__class__.__name__,
            feeds.LatestPostsFeed.__name__,
        )

    def test_post_detail_url(self):
        self.assertEqual(
            reverse(
                "post_detail",
                kwargs={"year": "2021", "month": "01", "day": "02", "pk": "123"},
            ),
            "/news/2021/01/02/123/",
        )

    def test_post_detail_view(self):
        self.assertEqual(
            resolve("/news/2021/01/02/123/").func.view_class, views.PostDetailView
        )

    def test_post_category_archive_url(self):
        self.assertEqual(
            reverse("post_category_archive", kwargs={"category_slug": "new-features"}),
            "/news/new-features/",
        )

    def test_post_category_archive_view(self):
        self.assertEqual(
            resolve("/news/new-features/").func.view_class,
            views.PostCategoryArchiveView,
        )

    def test_post_archive_url(self):
        self.assertEqual(reverse("news"), "/news/")

    def test_post_archive_view(self):
        self.assertEqual(resolve("/news/").func.view_class, views.PostArchiveView)
