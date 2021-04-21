import time

from freezegun import freeze_time

from django.http.cookie import SimpleCookie
from django.test import TestCase

from pepysdiary.common.utilities import make_datetime


EXPIRES_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


@freeze_time("2021-04-10 12:00:00", tz_offset=0)
class InitialViewTestCase(TestCase):
    "Tests for an initial view, with no previous visits"

    def setUp(self):
        self.client.get("/")
        self.cookies = self.client.cookies

    def test_visit_start_cookie_initial(self):
        "On an initial visit the visit_start cookie to should be set to NOW"
        self.assertIn("visit_start", self.cookies)
        self.assertEqual(self.cookies["visit_start"].value, str(int(time.time())))
        # 14 days ahead:
        self.assertEqual(
            self.cookies["visit_start"]["expires"],
            make_datetime("2021-04-24 12:00:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["visit_start"]["path"], "/")
        self.assertEqual(self.cookies["visit_start"]["max-age"], 1209601)

    def test_last_view_cookie_iniital(self):
        "On an initial visit the last_view cookie to should be set to NOW"
        self.assertIn("last_view", self.cookies)
        self.assertEqual(self.cookies["last_view"].value, str(int(time.time())))
        # 14 days ahead:
        self.assertEqual(
            self.cookies["last_view"]["expires"],
            make_datetime("2021-04-24 12:00:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["last_view"]["path"], "/")
        self.assertEqual(self.cookies["visit_start"]["max-age"], 1209601)

    def test_prev_visit_end_cookie_initial(self):
        "On an initial visit the prev_visit_end cookie should not be set"
        self.assertNotIn("prev_visit_end", self.cookies)


@freeze_time("2021-04-10 12:00:00", tz_offset=0)
class SecondViewTestCase(TestCase):
    "Tests for a second view in the same visit, no previous visits"

    def setUp(self):
        """
        We set the cookies that would have been set on the previous view.
        And then do the request for this view.
        """

        # Ten minutes ago:
        visit_start_time = make_datetime("2021-04-10 11:50:00")
        # Five minutes ago:
        last_view_time = make_datetime("2021-04-10 11:55:00")
        expires_time_str = make_datetime("2021-04-24 11:55:01").strftime(EXPIRES_FORMAT)

        self.client.cookies = SimpleCookie(
            {
                "visit_start": str(int(visit_start_time.timestamp())),
                "last_view": str(int(last_view_time.timestamp())),
            }
        )
        self.client.cookies["visit_start"]["expires"] = expires_time_str
        self.client.cookies["visit_start"]["path"] = "/"
        self.client.cookies["visit_start"]["max-age"] = 1209601

        self.client.cookies["last_view"]["expires"] = expires_time_str
        self.client.cookies["last_view"]["path"] = "/"
        self.client.cookies["last_view"]["max-age"] = 1209601

        self.client.get("/")
        self.cookies = self.client.cookies

    def test_visit_start_cookie_second_view(self):
        "On a second view in the same visit, visit_start cookie should remain the same"
        self.assertIn("visit_start", self.cookies)

        # Should be the same as the one set in setUp():
        self.assertEqual(
            self.cookies["visit_start"].value,
            str(int(make_datetime("2021-04-10 11:50:00").timestamp())),
        )
        self.assertEqual(
            self.cookies["visit_start"]["expires"],
            make_datetime("2021-04-24 11:55:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["visit_start"]["path"], "/")
        self.assertEqual(self.cookies["visit_start"]["max-age"], 1209601)

    def test_last_view_cookie_second_view(self):
        "On a second view in the same visit, last_view cookie should set to NOW"
        self.assertIn("last_view", self.cookies)
        self.assertEqual(self.cookies["last_view"].value, str(int(time.time())))
        # 14 days ahead:
        self.assertEqual(
            self.cookies["last_view"]["expires"],
            make_datetime("2021-04-24 12:00:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["last_view"]["path"], "/")
        self.assertEqual(self.cookies["visit_start"]["max-age"], 1209601)

    def test_prev_visit_end_cookie_second_view(self):
        "On a second view in the same visit, prev_visit_end should not be set"
        self.assertNotIn("prev_visit_end", self.cookies)


@freeze_time("2021-04-10 12:00:00", tz_offset=0)
class ReturnVisitTestCase(TestCase):
    "Tests for the first view of a new visit"

    def setUp(self):
        """
        We set the cookies that would have been set on the previous visit.
        And then do the request for this visit.
        """
        # Two days ago:
        visit_start_time = make_datetime("2021-04-08 12:00:00")
        last_view_time = make_datetime("2021-04-08 12:00:00")
        expires_time_str = make_datetime("2021-05-22 12:00:01").strftime(EXPIRES_FORMAT)

        self.client.cookies = SimpleCookie(
            {
                "visit_start": str(int(visit_start_time.timestamp())),
                "last_view": str(int(last_view_time.timestamp())),
            }
        )
        self.client.cookies["visit_start"]["expires"] = expires_time_str
        self.client.cookies["visit_start"]["path"] = "/"
        self.client.cookies["visit_start"]["max-age"] = 1209601

        self.client.cookies["last_view"]["expires"] = expires_time_str
        self.client.cookies["last_view"]["path"] = "/"
        self.client.cookies["last_view"]["max-age"] = 1209601

        self.client.get("/")
        self.cookies = self.client.cookies

    def test_visit_start_cookie_returning(self):
        "On a return visit the visit_start cookie should be set to NOW"
        self.assertIn("visit_start", self.cookies)
        self.assertEqual(self.cookies["visit_start"].value, str(int(time.time())))
        # 14 days ahead:
        self.assertEqual(
            self.cookies["visit_start"]["expires"],
            make_datetime("2021-04-24 12:00:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["visit_start"]["path"], "/")
        self.assertEqual(self.cookies["visit_start"]["max-age"], 1209601)

    def test_last_view_cookie_returning(self):
        "On a return visit the last_view cookie should be set to NOW"
        self.assertIn("last_view", self.cookies)
        self.assertEqual(self.cookies["last_view"].value, str(int(time.time())))
        # 14 days ahead:
        self.assertEqual(
            self.cookies["last_view"]["expires"],
            make_datetime("2021-04-24 12:00:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["last_view"]["path"], "/")
        self.assertEqual(self.cookies["visit_start"]["max-age"], 1209601)

    def test_prev_visit_end_cookie_returning(self):
        "On a return visit the prev_visit_end cookie should be set to last_view value"
        self.assertIn("prev_visit_end", self.cookies)
        self.assertEqual(
            self.cookies["prev_visit_end"].value,
            str(int(make_datetime("2021-04-08 12:00:00").timestamp())),
        )
        # 14 days ahead:
        self.assertEqual(
            self.cookies["prev_visit_end"]["expires"],
            make_datetime("2021-04-24 12:00:01").strftime(EXPIRES_FORMAT),
        )
        self.assertEqual(self.cookies["prev_visit_end"]["path"], "/")
        self.assertEqual(self.cookies["prev_visit_end"]["max-age"], 1209601)
