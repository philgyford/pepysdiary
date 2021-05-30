from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.letters import feeds
from pepysdiary.letters import views


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
            resolve("/letters/1660/01/01/my-letter/").func.__name__,
            views.LetterDetailView.__name__,
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
            resolve("/letters/person/123/").func.__name__,
            views.LetterPersonView.__name__,
        )

    def test_letter_archive_url(self):
        self.assertEqual(reverse("letters"), "/letters/")

    def test_letter_archive_view(self):
        self.assertEqual(
            resolve("/letters/").func.__name__, views.LetterArchiveView.__name__
        )
