from django.test import TestCase

from pepysdiary.common.templatetags.text_formatting_filters import (
    markup_tooltip,
    smartypants,
)


class SmartypantsTestCase(TestCase):
    def test_standard(self):
        val = smartypants("""'This is -- "a test"'""")
        self.assertEqual(val, "‘This is — “a test”’")

    def test_special_cases(self):
        "Our special cases should be replaced"
        cases = (
            ("the 'Change was", "the ’Change was"),
            ("the 'Chequer,", "the ’Chequer,"),
            ("a 'guinny, which", "a ’guinny, which"),
            ("a 'light which", "a ’light which"),
            ("not 'lighting, and", "not ’lighting, and"),
            ("a 'prentice was", "a ’prentice was"),
            ("once a 'Prentice of", "once a ’Prentice of"),
            ("the 'prentices were", "the ’prentices were"),
            ("the 'sparagus garden,", "the ’sparagus garden,"),
        )

        for case in cases:
            self.assertEqual(smartypants(case[0]), case[1])


class MarkupTooltipTestCase(TestCase):
    def test_does_nothing(self):
        val = markup_tooltip("12. Hello there.")
        self.assertEqual(val, "12. Hello there.")

    def test_finds_year_year(self):
        val = markup_tooltip("1601-1689. Hello there.")
        self.assertEqual(
            val,
            '<span itemprop="birthDate">1601</span>'
            '-<span itemprop="deathDate">1689</span>. Hello there.',
        )
