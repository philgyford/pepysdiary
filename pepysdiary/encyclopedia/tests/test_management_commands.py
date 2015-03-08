from mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils.six import StringIO

from pepysdiary.common.tests.test_base import PepysdiaryTestCase


class FetchWikipediaTest(PepysdiaryTestCase):
    """
    Tests for the management command that calls the
    TopicManager.fetch_wikipedia_texts() method. That method isn't tested here.
    """

    def test_no_args(self):
        with self.assertRaises(CommandError):
            call_command('fetch_wikipedia')

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_single_topic_id(self, fetch_method):
        call_command('fetch_wikipedia', '112', stdout=StringIO())
        fetch_method.assert_called_with(topic_ids=[112])

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_multiple_topic_ids(self, fetch_method):
        call_command('fetch_wikipedia', '112 344 6079', stdout=StringIO())
        fetch_method.assert_called_with(topic_ids=[112, 344, 6079])

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_all(self, fetch_method):
        call_command('fetch_wikipedia', all=True, stdout=StringIO())
        fetch_method.assert_called_with(topic_ids='all')

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_default_verbosity(self, fetch_method):
        out = StringIO()
        call_command('fetch_wikipedia', '112', stdout=out)
        self.assertIn('Done', out.getvalue())

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_zero_verbosity(self, fetch_method):
        out = StringIO()
        call_command('fetch_wikipedia', '112', verbosity=0, stdout=out)
        self.assertNotIn('Done', out.getvalue())


