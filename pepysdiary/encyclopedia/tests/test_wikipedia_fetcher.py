# coding: utf-8
from mock import patch
import responses
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from pepysdiary.common.tests.test_base import PepysdiaryTestCase
from pepysdiary.encyclopedia.wikipedia_fetcher import WikipediaFetcher

class FetchTest(PepysdiaryTestCase):

    source_html = '<p>Hello</p>'
    page_name = 'Edward_Montagu%2C_1st_Earl_of_Sandwich'

    def add_response(self, body, status=200):
        responses.add(
            responses.GET,
            'https://en.wikipedia.org/wiki/%s?action=render' % self.page_name,
            match_querystring=True,
            status=status,
            body=body
        )

    @responses.activate
    def test_it_sends_a_request(self):
        self.add_response(body=self.source_html)
        result = WikipediaFetcher().get_html(self.page_name)
        self.assertTrue(result['success'])
        self.assertEqual(result['content'], self.source_html)

    @responses.activate
    def test_it_handles_exceptions(self):
        errors = ( 
            (ConnectionError,   "Can't connect to domain."),
            (Timeout,           "Connection timed out."),
            (TooManyRedirects,  "Too many redirects."),
        ) 
        for error, message in errors:
            self.add_response(body=error())
            result = WikipediaFetcher().get_html(self.page_name)
            self.assertFalse(result['success'])
            self.assertEqual(result['content'], message)
            responses.reset()

    @responses.activate
    def test_it_handles_404s(self):
        self.add_response(body='<h1>Not found</h1>', status=404)
        result = WikipediaFetcher().get_html(self.page_name)
        self.assertFalse(result['success'])
        self.assertEqual(result['content'], 'HTTP Error: 404')

    @responses.activate
    def test_it_handles_500s(self):
        self.add_response(body='<h1>Not found</h1>', status=500)
        result = WikipediaFetcher().get_html(self.page_name)
        self.assertFalse(result['success'])
        self.assertEqual(result['content'], 'HTTP Error: 500')

    @responses.activate
    @patch('pepysdiary.encyclopedia.wikipedia_fetcher.WikipediaFetcher.filter_html')
    def test_it_filters_returned_html(self, filter_method):
        """
        Test that the fetch() method will pass the results of get_html() to
        filter_html() and then return the result.
        """
        # Our pretend WikipediaFetcher.filter_html() method should just
        # return what we pass into it:
        filter_method.return_value = self.source_html
        # When we pretend to call the URL in get_html() it'll return this:
        self.add_response(body=self.source_html)
        result = WikipediaFetcher().fetch(self.page_name)
        # Check filter_html() was called with what get_html() returned:
        filter_method.assert_called_with(self.source_html)
        # Whatever called fetch() should get this back:
        self.assertEqual(result, {'success': True, 'content': self.source_html})

    def test_filters_do_the_correct_thing(self):
        pass

