from django.test import TestCase

from pepysdiary.common.templatetags.utility_filters import to_class_name
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.letters.factories import LetterFactory


class ToClassNameTestCase(TestCase):
    def test_entry(self):
        self.assertEqual(to_class_name(EntryFactory(), "Entry"))

    def test_letter(self):
        self.assertEqual(to_class_name(LetterFactory(), "Letter"))

    def test_topic(self):
        self.assertEqual(to_class_name(TopicFactory(), "Topic"))
