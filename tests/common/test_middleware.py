import time

import time_machine
from django.http.cookie import SimpleCookie
from django.test import TestCase

from pepysdiary.common.utilities import make_datetime

# Format used for the cookies' expires parameter:
EXPIRES_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

# Value for cookies' max-age parameter.
# Based on VisitTimeMiddleware.cookie_duration.
# I don't know why it needs + 1.
MAX_AGE = (14 * 86400) + 1


class CookiesTestCase(TestCase):
    def _set_cookie_data(self, key, expires_time):
        self.client.cookies[key]["expires"] = expires_time.strftime(EXPIRES_FORMAT)
        self.client.cookies[key]["path"] = "/"
        self.client.cookies[key]["max-age"] = MAX_AGE


@time_machine.travel("2021-04-10 12:00:00 +0000", tick=False)
class InitialViewTestCase(CookiesTestCase):
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
        self.assertEqual(self.cookies["visit_start"]["max-age"], MAX_AGE)

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
        self.assertEqual(self.cookies["visit_start"]["max-age"], MAX_AGE)

    def test_prev_visit_end_cookie_initial(self):
        "On an initial visit the prev_visit_end cookie should not be set"
        self.assertNotIn("prev_visit_end", self.cookies)


@time_machine.travel("2021-04-10 12:00:00 +0000", tick=False)
class SecondViewTestCase(CookiesTestCase):
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
        expires_time = make_datetime("2021-04-24 11:55:01")

        self.client.cookies = SimpleCookie(
            {
                "visit_start": str(int(visit_start_time.timestamp())),
                "last_view": str(int(last_view_time.timestamp())),
            }
        )
        self._set_cookie_data("visit_start", expires_time)
        self._set_cookie_data("last_view", expires_time)
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
        self.assertEqual(self.cookies["visit_start"]["max-age"], MAX_AGE)

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
        self.assertEqual(self.cookies["visit_start"]["max-age"], MAX_AGE)

    def test_prev_visit_end_cookie_second_view(self):
        "On a second view in the same visit, prev_visit_end should not be set"
        self.assertNotIn("prev_visit_end", self.cookies)


@time_machine.travel("2021-04-10 12:00:00 +0000", tick=False)
class ReturnVisitTestCase(CookiesTestCase):
    "Tests for the first view of a new visit"

    def setUp(self):
        """
        We set the cookies that would have been set on the previous visit.
        And then do the request for this visit.
        """
        # Two days ago:
        visit_start_time = make_datetime("2021-04-08 12:00:00")
        last_view_time = make_datetime("2021-04-08 12:00:00")
        expires_time = make_datetime("2021-05-22 12:00:01")

        self.client.cookies = SimpleCookie(
            {
                "visit_start": str(int(visit_start_time.timestamp())),
                "last_view": str(int(last_view_time.timestamp())),
            }
        )
        self._set_cookie_data("visit_start", expires_time)
        self._set_cookie_data("last_view", expires_time)

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
        self.assertEqual(self.cookies["visit_start"]["max-age"], MAX_AGE)

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
        self.assertEqual(self.cookies["visit_start"]["max-age"], MAX_AGE)

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
        self.assertEqual(self.cookies["prev_visit_end"]["max-age"], MAX_AGE)


@time_machine.travel("2021-04-10 12:00:00 +0000", tick=False)
class InvalidCookiesTestCase(CookiesTestCase):
    "Testing what happens if cookies are already set but contain invalid data"

    def test_invalid_vist_start_cookie(self):
        "If visit_start cookie is invalid, visit_start should be set to NOW"

        # Same initial cookies as SecondViewTestCase but with an invalid
        # visit_start value.

        last_view_time = make_datetime("2021-04-10 11:55:00")
        expires_time = make_datetime("2021-04-24 11:55:01")

        self.client.cookies = SimpleCookie(
            {
                "visit_start": "not-a-date",
                "last_view": str(int(last_view_time.timestamp())),
            }
        )
        self._set_cookie_data("visit_start", expires_time)
        self._set_cookie_data("last_view", expires_time)
        self.client.get("/")

        self.assertIn("visit_start", self.client.cookies)
        self.assertEqual(
            self.client.cookies["visit_start"].value, str(int(time.time()))
        )

    def test_invalid_last_view_cookie(self):
        "If last_view cookie is invalid, last_view should be set to NOW"

        # Same initial cookies as SecondViewTestCase but with an invalid
        # last_view value.

        visit_start_time = make_datetime("2021-04-10 11:50:00")
        expires_time = make_datetime("2021-04-24 11:55:01")

        self.client.cookies = SimpleCookie(
            {
                "visit_start": str(int(visit_start_time.timestamp())),
                "last_view": "not-a-date",
            }
        )
        self._set_cookie_data("visit_start", expires_time)
        self._set_cookie_data("last_view", expires_time)
        self.client.get("/")

        self.assertIn("last_view", self.client.cookies)
        self.assertEqual(self.client.cookies["last_view"].value, str(int(time.time())))

    def test_invalid_prev_visit_end_cookie(self):
        "If prev_visit_end cookie is invalid, prev_visit_end should not be set"
        visit_start_time = make_datetime("2021-04-08 12:00:00")
        last_view_time = make_datetime("2021-04-08 12:00:00")
        expires_time = make_datetime("2021-05-22 12:00:01")

        self.client.cookies = SimpleCookie(
            {
                "visit_start": str(int(visit_start_time.timestamp())),
                "last_view": str(int(last_view_time.timestamp())),
                "prev_visit_end": "not-a-date",
            }
        )
        self._set_cookie_data("visit_start", expires_time)
        self._set_cookie_data("last_view", expires_time)
        self._set_cookie_data("prev_visit_end", expires_time)

        self.client.get("/")

        self.assertIn("prev_visit_end", self.client.cookies)
        self.assertEqual(
            self.client.cookies["prev_visit_end"].value,
            str(int(make_datetime("2021-04-08 12:00:00").timestamp())),
        )
