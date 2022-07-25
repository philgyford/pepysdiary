from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.encyclopedia import feeds, views


class EncyclopediaURLsTestCase(TestCase):
    """
    Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_encyclopedia_url(self):
        self.assertEqual(reverse("encyclopedia"), "/encyclopedia/")

    def test_encyclopedia_view(self):
        self.assertEqual(
            resolve("/encyclopedia/").func.view_class, views.EncyclopediaView
        )

    def test_topic_rss_url(self):
        self.assertEqual(reverse("topic_rss"), "/encyclopedia/rss/")

    def test_topic_rss_view(self):
        self.assertEqual(
            resolve("/encyclopedia/rss/").func.__class__.__name__,
            feeds.LatestTopicsFeed.__name__,
        )

    def test_topic_detail_url(self):
        self.assertEqual(
            reverse("topic_detail", kwargs={"pk": 123}), "/encyclopedia/123/"
        )

    def test_topic_detail_view(self):
        self.assertEqual(
            resolve("/encyclopedia/123/").func.view_class, views.TopicDetailView
        )

    def test_category_map_url(self):
        self.assertEqual(
            reverse("category_map", kwargs={"category_id": 123}),
            "/encyclopedia/map/123/",
        )

    def test_category_map_view(self):
        self.assertEqual(
            resolve("/encyclopedia/map/123/").func.view_class, views.CategoryMapView
        )

    def test_category_detail_url(self):
        self.assertEqual(
            reverse(
                "category_detail", kwargs={"slugs": "animals/domestic-dogs/terriers"}
            ),
            "/encyclopedia/animals/domestic-dogs/terriers/",
        )

    def test_category_detail_view(self):
        self.assertEqual(
            resolve("/encyclopedia/animals/domestic-dogs/terriers/").func.view_class,
            views.CategoryDetailView,
        )
