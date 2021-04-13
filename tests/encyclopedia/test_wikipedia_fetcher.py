from unittest.mock import patch
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import responses

from django.test import TestCase

from pepysdiary.encyclopedia.wikipedia_fetcher import WikipediaFetcher


class FetchTestCase(TestCase):

    source_html = "<p>Hello</p>"
    page_name = "Edward_Montagu%2C_1st_Earl_of_Sandwich"

    def add_response(self, body, status=200):
        responses.add(
            responses.GET,
            "https://en.wikipedia.org/wiki/%s?action=render" % self.page_name,
            match_querystring=True,
            status=status,
            body=body,
        )

    @responses.activate
    def test_it_sends_a_request(self):
        self.add_response(body=self.source_html)
        result = WikipediaFetcher()._get_html(self.page_name)
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], self.source_html)

    @responses.activate
    def test_it_handles_exceptions(self):
        errors = (
            (ConnectionError, "Can't connect to domain."),
            (Timeout, "Connection timed out."),
            (TooManyRedirects, "Too many redirects."),
        )
        for error, message in errors:
            self.add_response(body=error())
            result = WikipediaFetcher()._get_html(self.page_name)
            self.assertFalse(result["success"])
            self.assertEqual(result["content"], message)
            responses.reset()

    @responses.activate
    def test_it_handles_404s(self):
        self.add_response(body="<h1>Not found</h1>", status=404)
        result = WikipediaFetcher()._get_html(self.page_name)
        self.assertFalse(result["success"])
        self.assertEqual(result["content"], "HTTP Error: 404")

    @responses.activate
    def test_it_handles_500s(self):
        self.add_response(body="<h1>Not found</h1>", status=500)
        result = WikipediaFetcher()._get_html(self.page_name)
        self.assertFalse(result["success"])
        self.assertEqual(result["content"], "HTTP Error: 500")

    @responses.activate
    @patch("pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher._tidy_html")
    def test_it_filters_returned_html(self, filter_method):
        """
        Test that the fetch() method will pass the results of _get_html() to
        _tidy_html() and then return the result.
        """
        # Our pretend WikipediaFetcher._tidy_html() method should just
        # return what we pass into it:
        filter_method.return_value = self.source_html
        # When we pretend to call the URL in _get_html() it'll return this:
        self.add_response(body=self.source_html)
        result = WikipediaFetcher().fetch(self.page_name)
        # Check _tidy_html() was called with what _get_html() returned:
        filter_method.assert_called_with(self.source_html)
        # Whatever called fetch() should get this back:
        self.assertEqual(result, {"success": True, "content": self.source_html})

    def test_it_removes_disallowed_tags(self):
        """
        Note: This test currently works if the BeautifulSoup parser is "lxml", which
        will add the extra <p></p> tags. "html.parser" won't.
        """
        in_html = "<blink>Blinking</blink> <strong>Bold</strong>"
        out_html = "<p>Blinking <strong>Bold</strong></p>"
        self.assertEqual(WikipediaFetcher()._tidy_html(in_html), out_html)

    def test_it_removes_disallowed_attributes(self):
        in_html = '<a class="my-class" href="test.html" ' 'data-bad="My data">Link</a>'
        out_html = '<a class="my-class" href="test.html">Link</a>'
        self.assertEqual(WikipediaFetcher()._tidy_html(in_html), out_html)

    def test_it_removes_disallowed_selectors(self):
        in_html = (
            "<div>This is OK</div>"
            '<div class="navbar mini">This is not</div>'
            "<div>This is also fine</div>"
            '<div class="mini navbar">This is not either</div>'
        )
        out_html = "<div>This is OK</div><div>This is also fine</div>"
        self.assertEqual(WikipediaFetcher()._strip_html(in_html), out_html)

    def test_it_removes_disallowed_classes(self):
        in_html = (
            '<div>This is OK</div><div class="noprint">This is not'
            '</div><div>This is also fine</div><p class="noprint">This '
            "is not either</p>"
        )
        out_html = "<div>This is OK</div><div>This is also fine</div>"
        self.assertEqual(WikipediaFetcher()._strip_html(in_html), out_html)

    def test_it_adds_classes(self):
        in_html = (
            '<div class="infobox">Infobox</div>'
            '<div class="bibble">Untouched</div>'
            '<div class="infobox">Infobox 2</div>'
        )
        out_html = (
            '<div class="infobox table table-bordered">Infobox</div>'
            '<div class="bibble">Untouched</div>'
            '<div class="infobox table table-bordered">Infobox 2'
            "</div>"
        )
        self.assertEqual(WikipediaFetcher()._strip_html(in_html), out_html)

    def test_it_removes_scripts(self):
        "All <script> tags and contents should be removed."
        in_html = (
            '<div class="bibble">'
            '<script>console.log("This should be removed.")</script>'
            "This should show up."
            "</div>"
        )
        out_html = '<div class="bibble">This should show up.</div>'
        self.assertEqual(WikipediaFetcher()._strip_html(in_html), out_html)
