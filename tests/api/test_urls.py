from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.api import views


class DiaryURLsTestCase(TestCase):
    def test_root_url(self):
        self.assertEqual(reverse("api:root"), "/api/v1/")

    def test_root_view(self):
        self.assertEqual(resolve("/api/v1/").func.__name__, views.api_root.__name__)

    def test_category_list_url(self):
        self.assertEqual(reverse("api:category_list"), "/api/v1/categories/")

    def test_category_list_view(self):
        self.assertEqual(
            resolve("/api/v1/categories/").func.__name__,
            views.CategoryListView.__name__,
        )

    def test_category_detail_url(self):
        self.assertEqual(
            reverse("api:category_detail", kwargs={"category_slug": "cocker-spaniels"}),
            "/api/v1/categories/cocker-spaniels/",
        )

    def test_category_detail_view(self):
        self.assertEqual(
            resolve("/api/v1/categories/cocker-spaniels/").func.__name__,
            views.CategoryDetailView.__name__,
        )

    def test_entry_list_url(self):
        self.assertEqual(reverse("api:entry_list"), "/api/v1/entries/")

    def test_entry_list_view(self):
        self.assertEqual(
            resolve("/api/v1/entries/").func.__name__,
            views.EntryListView.__name__,
        )

    def test_entry_detail_url(self):
        self.assertEqual(
            reverse("api:entry_detail", kwargs={"entry_date": "1660-01-02"}),
            "/api/v1/entries/1660-01-02/",
        )

    def test_entry_detail_view(self):
        self.assertEqual(
            resolve("/api/v1/entries/1660-01-02/").func.__name__,
            views.EntryDetailView.__name__,
        )

    def test_topic_list_url(self):
        self.assertEqual(reverse("api:topic_list"), "/api/v1/topics/")

    def test_topic_list_view(self):
        self.assertEqual(
            resolve("/api/v1/topics/").func.__name__,
            views.TopicListView.__name__,
        )

    def test_topic_detail_url(self):
        self.assertEqual(
            reverse("api:topic_detail", kwargs={"topic_id": "123"}),
            "/api/v1/topics/123/",
        )

    def test_topic_detail_view(self):
        self.assertEqual(
            resolve("/api/v1/topics/123/").func.__name__,
            views.TopicDetailView.__name__,
        )
