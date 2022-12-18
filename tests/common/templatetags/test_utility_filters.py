from django.test import TestCase

from pepysdiary.common.templatetags.utility_filters import ordinal_word, to_class_name
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.letters.factories import LetterFactory


class ToClassNameTestCase(TestCase):
    def test_entry(self):
        self.assertEqual(to_class_name(EntryFactory()), "Entry")

    def test_letter(self):
        self.assertEqual(to_class_name(LetterFactory()), "Letter")

    def test_topic(self):
        self.assertEqual(to_class_name(TopicFactory()), "Topic")


class OrdinalWordTestCase(TestCase):
    def test_numbers(self):
        terms = {
            # Terms set in the function:
            1: "first",
            2: "second",
            3: "third",
            4: "fourth",
            5: "fifth",
            6: "sixth",
            7: "seventh",
            8: "eighth",
            9: "ningth",
            10: "tenth",
            # Terms that come from the standard ordinal template filter:
            11: "11th",
            20: "20th",
            21: "21st",
            1234: "1234th",
        }

        for num, term in terms.items():
            self.assertEqual(ordinal_word(num), term)
