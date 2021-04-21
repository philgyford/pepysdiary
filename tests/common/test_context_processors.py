from freezegun import freeze_time

from django.conf import settings
from django.test import Client, override_settings, RequestFactory, TestCase

from pepysdiary.common.context_processors import (
    api_keys,
    config,
    date_formats,
    url_name,
)
from pepysdiary.common.factories import ConfigFactory
from pepysdiary.common.utilities import make_datetime


class RequestTestCase(TestCase):
    "Parent class that defines a request object"

    def setUp(self):
        self.factory = RequestFactory()
        # We use '/fake-path/' for all tests because not testing URLs here,
        # and the context_processors don't care what the URL is.
        self.request = self.factory.get("/fake-path/")


class APIKeysTestCase(RequestTestCase):
    @override_settings(MAPBOX_MAP_ID="1234")
    def test_mapbox_map_id(self):
        "If the MAPBOX_MAP_ID setting is set it should be returned in the context"
        context = api_keys(self.request)
        self.assertIn("MAPBOX_MAP_ID", context)
        self.assertEqual(context["MAPBOX_MAP_ID"], "1234")

    @override_settings()
    def test_mapbox_map_id_not_set(self):
        "If the MAPBOX_MAP_ID setting is not set that key should not be returned"
        del settings.MAPBOX_MAP_ID
        context = api_keys(self.request)
        self.assertNotIn("MAPBOX_MAP_ID", context)

    @override_settings(MAPBOX_ACCESS_TOKEN="1234")
    def test_mapbox_access_token(self):
        "If the MAPBOX_ACCESS_TOKEN setting is set it should be returned in the context"
        context = api_keys(self.request)
        self.assertIn("MAPBOX_ACCESS_TOKEN", context)
        self.assertEqual(context["MAPBOX_ACCESS_TOKEN"], "1234")

    @override_settings()
    def test_mapbox_access_token_not_set(self):
        "If the MAPBOX_ACCESS_TOKEN setting is not set that key should not be returned"
        del settings.MAPBOX_ACCESS_TOKEN
        context = api_keys(self.request)
        self.assertNotIn("MAPBOX_ACCESS_TOKEN", context)

    @override_settings(GOOGLE_ANALYTICS_ID="1234")
    def test_google_analytics_id(self):
        "If the GOOGLE_ANALYTICS_ID setting is set it should be returned in the context"
        context = api_keys(self.request)
        self.assertIn("GOOGLE_ANALYTICS_ID", context)
        self.assertEqual(context["GOOGLE_ANALYTICS_ID"], "1234")

    @override_settings()
    def test_google_analytics_id_not_set(self):
        "If the GOOGLE_ANALYTICS_ID setting is not set that key should not be returned"
        del settings.GOOGLE_ANALYTICS_ID
        context = api_keys(self.request)
        self.assertNotIn("GOOGLE_ANALYTICS_ID", context)


class ConfigTestCase(RequestTestCase):
    def test_config(self):
        "It should return the current Config object"
        ConfigFactory(registration_question="Tester!")
        context = config(self.request)
        self.assertIn("config", context)
        self.assertEqual(context["config"].registration_question, "Tester!")


class DateFormatsTestCase(RequestTestCase):
    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    def test_date_formats(self):
        "It should return the correct keys"
        context = date_formats(self.request)

        self.assertIn("date_format_longest", context)
        self.assertIn("date_format_long", context)
        self.assertIn("date_format_long_strftime", context)
        self.assertIn("date_format_mid", context)
        self.assertIn("date_format_mid_strftime", context)
        self.assertIn("time_format", context)
        self.assertIn("time_format_strftime", context)

        self.assertIn("time_now", context)
        self.assertEqual(context["time_now"], make_datetime("2021-04-10 12:00:00"))


class URLNameTestCase(RequestTestCase):
    """
    For some reason request.resolver_match, in url_name() is always
    None when I test this using only the request.

    So we need to rely on the response from the Client() request in
    order to do this test.

    Which is going to fail if the url_name contexxt processor isn't
    enabled in settings.k
    """

    def test_url_name(self):
        "If the URL exists it should return the URL's name"
        response = Client().get("/")
        self.assertIn("url_name", response.context)
        self.assertEqual(response.context["url_name"], "home")

        # request = self.factory.get("/")
        # context = url_name(request)
        # self.assertIn("url_name", context)
        # self.assertEqual(context["url_name"], "home")

    def test_url_name_does_not_exist(self):
        "If the URL doesn't exist it should return False"
        response = Client().get("/does-not-exist")
        self.assertIn("url_name", response.context)
        self.assertFalse(response.context["url_name"])

        # request = self.factory.get("/does-not-exist/")
        # context = url_name(request)
        # self.assertIn("url_name", context)
        # self.assertFalse(context["url_name"])
