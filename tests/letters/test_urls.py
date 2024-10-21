from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.letters import feeds, views


class DiaryURLsTestCase(TestCase):
    """Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_letter_rss_url(self):
        self.assertEqual(reverse("letter_rss"), "/letters/rss/")

    def test_letter_rss_view(self):
        self.assertEqual(
            resolve("/letters/rss/").func.__class__.__name__,
            feeds.LatestLettersFeed.__name__,
        )

    def test_letter_detail_url(self):
        self.assertEqual(
            reverse(
                "letter_detail",
                kwargs={
                    "year": "1660",
                    "month": "01",
                    "day": "01",
                    "slug": "my-letter",
                },
            ),
            "/letters/1660/01/01/my-letter/",
        )

    def test_letter_detail_view(self):
        self.assertEqual(
            resolve("/letters/1660/01/01/my-letter/").func.view_class,
            views.LetterDetailView,
        )

    def test_letter_from_person_url(self):
        self.assertEqual(
            reverse(
                "letter_from_person",
                kwargs={"pk": "123"},
            ),
            "/letters/person/from/123/",
        )

    def test_letter_from_person_view(self):
        self.assertEqual(
            resolve("/letters/person/from/123/").func.view_class,
            views.LetterFromPersonView,
        )

    def test_letter_to_person_url(self):
        self.assertEqual(
            reverse(
                "letter_to_person",
                kwargs={"pk": "123"},
            ),
            "/letters/person/to/123/",
        )

    def test_letter_to_person_view(self):
        self.assertEqual(
            resolve("/letters/person/to/123/").func.view_class, views.LetterToPersonView
        )

    def test_letter_person_url(self):
        self.assertEqual(
            reverse(
                "letter_person",
                kwargs={"pk": "123"},
            ),
            "/letters/person/123/",
        )

    def test_letter_person_view(self):
        self.assertEqual(
            resolve("/letters/person/123/").func.view_class, views.LetterPersonView
        )

    def test_letter_archive_url(self):
        self.assertEqual(reverse("letters"), "/letters/")

    def test_letter_archive_view(self):
        self.assertEqual(resolve("/letters/").func.view_class, views.LetterArchiveView)
