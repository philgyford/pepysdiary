from pepysdiary.common.templatetags.text_formatting_filters import (
    markup_tooltip,
    smartypants,
)
from .test_base import PepysdiaryTestCase


class SmartypantsTestCase(PepysdiaryTestCase):
    def test_standard(self):
        val = smartypants("""'This is -- "a test"'""")
        self.assertEqual(val, "&#8216;This is &#8212; &#8220;a test&#8221;&#8217;")

    def test_special_cases(self):
        "Our special cases should be replaced"
        cases = (
            ("the 'Change was", "the &#8217;Change was"),
            ("the 'Chequer,", "the &#8217;Chequer,"),
            ("a 'guinny, which", "a &#8217;guinny, which"),
            ("a 'light which", "a &#8217;light which"),
            ("not 'lighting, and", "not &#8217;lighting, and"),
            ("a 'prentice was", "a &#8217;prentice was"),
            ("the 'prentices were", "the &#8217;prentices were"),
            ("the 'sparagus garden,", "the &#8217;sparagus garden,")
        )

        for case in cases:
            self.assertEqual(smartypants(case[0]), case[1])


class MarkupTooltipTestCase(PepysdiaryTestCase):
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
