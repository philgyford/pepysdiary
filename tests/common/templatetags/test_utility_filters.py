import re

from django.test import TestCase

from pepysdiary.common.templatetags.utility_filters import (
    custom_urlizetrunc,
    ordinal_word,
    to_class_name,
)
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


class CustomUrlizeTruncTestCase(TestCase):
    def test_basic_truncation(self):
        comment = "Check this: https://example.com/a-very-long-url"
        result = custom_urlizetrunc(comment, 20)
        self.assertIn('<a href="https://example.com/a-very-long-url"', result)
        self.assertIn(">example.com/a-very-…</a>", result)

    def test_apostrophe_escaping(self):
        comment = "Wow! https://example.com/O'Connor"
        result = custom_urlizetrunc(comment, 50)
        self.assertIn("O%27Connor", result)

    def test_http_removal_in_visible_text(self):
        comment = "Visit https://example.com for details."
        result = custom_urlizetrunc(comment, 30)
        self.assertIn('<a href="https://example.com"', result)
        self.assertIn(">example.com</a>", result)

    def test_www_url_truncation(self):
        comment = "Check this: www.example.com/long-url"
        result = custom_urlizetrunc(comment, 20)
        self.assertIn('<a href="http://www.example.com/long-url"', result)
        self.assertIn(">www.example.com/lon…</a>", result)

    def test_multiple_identical_links(self):
        comment = "Link: https://example.com/test and another https://example.com/test"
        result = custom_urlizetrunc(comment, 15)
        self.assertEqual(result.count(">example.com/te…</a>"), 2)

    def test_mixed_text_and_links(self):
        comment = "Comment with https://example.com/a/long/path and some more text."
        result = custom_urlizetrunc(comment, 20)
        self.assertIn('<a href="https://example.com/a/long/path"', result)
        self.assertIn(">example.com/a/long/…</a>", result)

    def test_long_url_with_query_params(self):
        comment = "Here: https://example.com/path?query=1&value=2&count=3"
        result = custom_urlizetrunc(comment, 34)
        self.assertIn(">example.com/path?query=1&value=2&…</a>", result)

    def test_url_with_link_to_highlight(self):
        comment = "Here is a link to the page I was talking about https://threedecks.org/index.php?display_type=show_ship&id=2790#:~:text=British%20Fifth%20Rate%20ship%20'Nightingale'%20(1651).%20Dates%20of,armament,%20commanders,%20officers%20and%20crewmen,%20actions,%20battles,%20sources"
        result = custom_urlizetrunc(comment, 34)
        self.assertIn(">threedecks.org/index.php?display_…</a>", result)

    def test_archive_dot_org_url(self):
        comment = "THE ART OF MARBLE WORKING IN GENERAL link on the Wayback Machine:\
        https://web.archive.org/web/20070208095349/http://www.cagenweb.com/quarries/articles_and_books/marble_workers_manual/mwh-p2_sect1.html"
        result = custom_urlizetrunc(comment, 34)
        self.assertIn("web.archive.org/web/2007020809534…", result)

    def test_truncation_of_multiple_urls(self):
        urls = [
          "http://foo.com/blah_blah/baz/bar",
          "http://foo.com/blah_blah/baz/bar/",
          "http://foo.com/blah_blah_(wikipedia)",
          "http://foo.com/blah_blah_(wikipedia)_(again)",
          "http://www.example.com/wpstyle/?p=364",
          "http://www.example.com/foo/?bar=baz&inga=42&quux",
          "http://userid:password@example.com:8080",
          "http://userid:password@example.com:8080/",
          "http://userid@example.com/restricted",
          "http://userid@example.com/restricted/",
          "http://userid@example.com:8080",
          "http://userid@example.com:8080/",
          "http://userid:password@example.com",
          "http://userid:password@example.com/",
          "http://142.42.1.1/dictionary/wine/index.ssf?DEF_ID=2630&ISWINE=T",
          "http://142.42.1.1:8080/e/eebo2/B02904.0001.001?view=toc",
          "http://foo.com/blah_(wikipedia)#cite-1",
          "http://foo.com/blah_(wikipedia)_blah#cite-1",
          "http://foo.com/unicode_(✪)_in_parens",
          "http://foo.com/(something)?after=parens",
          "http://code.google.com/events/#&product=browser",
          "https://shop.nationalarchives.gov.uk/products/a-z-charles-iis-london-1682?utm_source=emailmarketing&utm_medium=email&utm_campaign=shop_historic_london_azs&utm_content=2021-08-28",
          "http://foo.bar/?q=Test%20URL-encoded%20stuff",
          "dict.leo.org/ende?lp=ende&lang=de&searchLoc=0&cmpType=relaxed&sectHdr=on",
          "https://l.macys.com/new-york-ny/managers/valerie/perfumes/esquivel.html?ref=true",
        ]

        for url in urls:
            cleaned_url = re.sub(r"^https?://", "", url)
            expected_truncated = cleaned_url[:19] + "…"
            result = custom_urlizetrunc(url, 20)
            self.assertIn(expected_truncated, result)
