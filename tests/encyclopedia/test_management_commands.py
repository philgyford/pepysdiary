from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

from ..common.test_base import PepysdiaryTestCase


class FetchWikipediaTest(PepysdiaryTestCase):
    """
    Tests for the management command that calls the
    TopicManager.fetch_wikipedia_texts() method. That method isn't tested here.
    """

    def test_no_args(self):
        with self.assertRaises(CommandError):
            call_command("fetch_wikipedia")

    def test_wrong_args(self):
        with self.assertRaises(CommandError):
            call_command("fetch_wikipedia", "all")

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_single_topic_id(self, fetch_method):
        call_command("fetch_wikipedia", ids=[112], stdout=StringIO())
        fetch_method.assert_called_with(topic_ids=[112])

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_multiple_topic_ids(self, fetch_method):
        call_command("fetch_wikipedia", ids=[112, 344, 6079], stdout=StringIO())
        fetch_method.assert_called_with(topic_ids=[112, 344, 6079])

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_all(self, fetch_method):
        call_command("fetch_wikipedia", all=True, stdout=StringIO())
        fetch_method.assert_called_with(num="all")

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_num(self, fetch_method):
        call_command("fetch_wikipedia", num=30, stdout=StringIO())
        fetch_method.assert_called_with(num=30)

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_default_verbosity(self, fetch_method):
        #  What the mocked method will return:
        fetch_method.side_effect = [{"success": [112], "failure": []}]
        out = StringIO()
        call_command("fetch_wikipedia", ids=[112], stdout=out)
        self.assertIn("Successfully fetched 1 topic(s)", out.getvalue())

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_zero_verbosity(self, fetch_method):
        #  What the mocked method will return:
        fetch_method.side_effect = [{"success": [112], "failure": []}]
        out = StringIO()
        call_command("fetch_wikipedia", ids=[112], verbosity=0, stdout=out)
        self.assertNotIn("Successfully fetched 1 topic(s)", out.getvalue())

    @patch("pepysdiary.encyclopedia.models.TopicManager.fetch_wikipedia_texts")
    def test_with_extra_verbosity(self, fetch_method):
        #  What the mocked method will return:
        fetch_method.side_effect = [{"success": [112, 150], "failure": [344]}]
        out = StringIO()
        out_err = StringIO()
        call_command(
            "fetch_wikipedia",
            ids=[112, 344, 150],
            verbosity=2,
            stdout=out,
            stderr=out_err,
        )
        self.assertIn("Successfully fetched 2 topic(s)", out.getvalue())
        self.assertIn("IDs: 112, 150", out.getvalue())
        self.assertIn(
            "Tried and failed to fetch texts for 1 topic(s)", out_err.getvalue()
        )
        self.assertIn("IDs: 344", out_err.getvalue())
