from django.test import RequestFactory, TestCase, TransactionTestCase


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
