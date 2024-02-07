from xml.dom import minidom

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import RequestFactory, TestCase, TransactionTestCase


class FeedTestCase(TestCase):
    """
    Borrowing some handy methods from
    https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
    """

    def setUp(self):
        super().setUp()
        # For some reason we need to set this or else, when we run
        # *all* the tests then the domain name is set to the same
        # as the Site object for the dev site in Docker. But not when
        # we only run the feed tests specifically. Weird.
        site = Site.objects.first()
        site.domain = "example.com"
        site.save()
        cache.clear()

    def get_feed_element(self, url):
        response = self.client.get(url)
        doc = minidom.parseString(response.content)

        feed_elem = doc.getElementsByTagName("rss")
        self.assertEqual(len(feed_elem), 1)
        feed = feed_elem[0]

        return feed

    def get_channel_element(self, url):
        """Handy method that returns the 'channel' tag from a feed at url.
        You can then get the items like:

            chan = self.get_channel_element('/blah/')
            items = chan.getElementsByTagName('item')
        """
        feed = self.get_feed_element(url)

        chan_elem = feed.getElementsByTagName("channel")
        self.assertEqual(len(chan_elem), 1)
        chan = chan_elem[0]

        return chan

    def assertChildNodes(self, elem, expected):  # noqa: N802
        actual = {n.nodeName for n in elem.childNodes}
        expected = set(expected)
        self.assertEqual(actual, expected)

    def assertChildNodeContent(self, elem, expected):  # noqa: N802
        for k, v in expected.items():
            # It appears that minidom will make a node with no text
            # None, rather than an element. So when we try to get its
            # wholeText, we get an AttributeError.
            # So here we try to work around that...
            first_child = elem.getElementsByTagName(k)[0].firstChild
            try:
                test_value = first_child.wholeText
            except AttributeError:
                test_value = ""

            try:
                self.assertEqual(test_value, v)
            except IndexError as err:
                msg = f"{err} for '{k}' and '{v}'"
                raise IndexError(msg) from err

    def assertCategories(self, elem, expected):  # noqa: N802
        self.assertEqual(
            {
                i.firstChild.wholeText
                for i in elem.childNodes
                if i.nodeName == "category"
            },
            set(expected),
        )


class ViewTestCase(TestCase):
    """
    Parent class to use with all the other view test cases.
    """

    def setUp(self):
        self.factory = RequestFactory()
        # We use '/fake-path/' for all tests because not testing URLs here,
        # and the views don't care what the URL is.
        self.request = self.factory.get("/fake-path/")


class ViewTransactionTestCase(TransactionTestCase):
    """
    Same as ViewTestCase but with a different parent.

    Need to use TransactionTestCase for the SearchView tests because setting the
    search_vectors on objects requires transaction.on_commit() to work, which it
    doesn't with the standard TestCase.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/fake-path/")
