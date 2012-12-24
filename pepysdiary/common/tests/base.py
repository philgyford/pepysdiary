import logging

from django.test import TestCase


# Not sure of the best place for this.
logging.disable(logging.ERROR)


class PepysdiaryTestCase(TestCase):
    """
    Should be the parent for all other TestCases.
    """
    fixtures = [
        'auth_testdata',
        'sites_testdata',
    ]
