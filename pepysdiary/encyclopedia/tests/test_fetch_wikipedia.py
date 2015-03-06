from mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO


class ArgumentsTest(TestCase):
    # ./manage.py dumpdata encyclopedia.Topic --pks=344,112,6079 --indent 4 > pepysdiary/encyclopedia/fixtures/wikipedia_test.json
    fixtures = ['wikipedia_test.json']

    def test_no_args(self):
        with self.assertRaises(CommandError):
            call_command('fetch_wikipedia')

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_topic_ids(self, fetch_method):
        call_command('fetch_wikipedia', '112', stdout=StringIO())
        fetch_method.assert_called_with('112')

    @patch('pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts')
    def test_with_all(self, fetch_method):
        call_command('fetch_wikipedia', all=True, stdout=StringIO())
        fetch_method.assert_called_with('all')

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


