# coding: utf-8
from pepysdiary.common.tests.test_base import PepysdiaryTestCase

from pepysdiary.common.templatetags.text_formatting_filters import markup_tooltip


class MarkupTooltipTestCase(PepysdiaryTestCase):

    def test_does_nothing(self):
        val = markup_tooltip("12. Hello there.")
        self.assertEqual(val, "12. Hello there.")

    def test_finds_year_year(self):
        val = markup_tooltip("1601-1689. Hello there.")
        self.assertEqual(val, '<span itemprop="birthDate">1601</span>-<span itemprop="deathDate">1689</span>. Hello there.')

