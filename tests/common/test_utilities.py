from datetime import datetime

import pytz
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings

from pepysdiary.common.utilities import (
    fix_old_links,
    get_day,
    get_day_e,
    get_month,
    get_month_b,
    get_year,
    hilite_words,
    is_leap_year,
    make_date,
    make_datetime,
    make_url_absolute,
    smart_truncate,
    trim_hilites,
)


class MakeDateTestCase(TestCase):
    def test_make_date(self):
        self.assertEqual(
            make_date("2021-02-01"), datetime.strptime("2021-02-01", "%Y-%m-%d").date()
        )


class MakeDateTimeTestCase(TestCase):
    def test_make_date(self):
        self.assertEqual(
            make_datetime("2021-02-01 12:00:00"),
            datetime.strptime("2021-02-01 12:00:00", "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=pytz.utc
            ),
        )


class SmartTruncateTestCase(TestCase):
    def test_short_string(self):
        "Does nothing if string is shorter than length"
        self.assertEqual(smart_truncate("Hello"), "Hello")

    def test_default_length(self):
        "Truncates at 80 characters by default"
        s = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Etiam vitae erat blandit, malesuada sem."
        )
        self.assertEqual(
            smart_truncate(s),
            (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Etiam vitae erat…"
            ),
        )

    def test_custom_length(self):
        "Truncates at whatever length is supplied"
        s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        self.assertEqual(smart_truncate(s, 20), "Lorem ipsum dolor…")

    def test_custom_suffix(self):
        "It should use a custom suffix if supplied"
        s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        self.assertEqual(smart_truncate(s, 20, " –"), "Lorem ipsum dolor –")


class HiliteWordsTestCase(TestCase):
    def test_hilite_word(self):
        "It should hilite a matching word"
        s = "This is my test"
        self.assertEqual(hilite_words(s, "my"), "This is <b>my</b> test")

    def test_hilite_words(self):
        "It should hilite all matching words"
        s = "This is my test"
        self.assertEqual(hilite_words(s, "This my"), "<b>This</b> is <b>my</b> test")

    def test_hilite_case_insensitive(self):
        "It should ignore case"
        s = "This is my test"
        self.assertEqual(hilite_words(s, "this MY"), "<b>This</b> is <b>my</b> test")

    def test_no_match(self):
        "It should return the text as-is if there's no match"
        s = "This is my test"
        self.assertEqual(hilite_words(s, "parrots"), "This is my test")

    def test_strips_html(self):
        "It should strip any existing HTML"
        s = "<i>This</i> is my test"
        self.assertEqual(hilite_words(s, "my"), "This is <b>my</b> test")

    def test_ignores_spaces(self):
        "It should ignore extra spaces around the supplied words"
        s = "This is my test"
        self.assertEqual(
            hilite_words(s, "    This     my     "), "<b>This</b> is <b>my</b> test"
        )

    def test_ignores_punctuation(self):
        s = "This is my test"
        self.assertEqual(hilite_words(s, '"is"my"'), "This <b>is</b> <b>my</b> test")

    def test_plurals(self):
        "It should hilite matches with an extra s"
        s = "I like cats a lot"
        self.assertEqual(hilite_words(s, "cat"), "I like <b>cats</b> a lot")


class TrimHilitesTestCase(TestCase):
    def test_trims(self):
        "It should trim around a hilite"
        s = "This is my <b>test</b> here."
        result = trim_hilites(s, 5, 8)
        self.assertEqual(result["html"], "… s my <b>test</b> here.")

    def test_end(self):
        "It should add ellipsis on the end if necessary."
        s = "This is my <b>test</b> which goes on a bit."
        result = trim_hilites(s, 5, 8)
        self.assertEqual(result["html"], "… s my <b>test</b> which g …")

    def test_groups(self):
        "It should keep nearby hilites together"
        s = "This <b>is</b> my <b>test</b> and it goes on <b>a</b> bit"
        result = trim_hilites(s, 5, 8)
        self.assertEqual(
            result["html"],
            "This <b>is</b> my <b>test</b> and it … s on <b>a</b> bit",
        )

    def test_groups_2(self):
        "It should handle multiple hilites within range of each other."
        s = "This <b>is</b> my <b>test</b> <b>and</b> it goes on a bit like this."
        result = trim_hilites(s, chars_before=5, chars_after=20)
        self.assertEqual(
            result["html"],
            "This <b>is</b> my <b>test</b> <b>and</b> it goes on a bit li …",
        )

    def test_no_hilites_default(self):
        "It should return nothing if there are no hilites."
        result = trim_hilites("Hello")
        self.assertEqual(result["html"], "")

    def test_no_hilites_allow_empty_false(self):
        "It should return the start of the text if there are no hilites"
        s = "This is my text that has no hilites in it at all"
        result = trim_hilites(s, chars_before=5, chars_after=8, allow_empty=False)
        self.assertEqual(
            result["html"],
            "This is my te … ",
        )

    def test_max_hilites(self):
        "It should only show the number of hilites requested"
        s = "Hi <b>test</b> some words <b>test</b> and more here <b>test</b>"
        result = trim_hilites(s, 3, 3, max_hilites_to_show=2)
        self.assertEqual(result["html"], "Hi <b>test</b> so … ds <b>test</b> an")
        self.assertEqual(result["hilites_shown"], 2)
        self.assertEqual(result["total_hilites"], 3)


class IsLeapYearTestCase(TestCase):
    def test_is_leap_year_true(self):
        self.assertTrue(is_leap_year(1600))
        self.assertTrue(is_leap_year(1980))
        self.assertTrue(is_leap_year(2000))

    def test_is_leap_year_false(self):
        self.assertFalse(is_leap_year(1700))
        self.assertFalse(is_leap_year(1800))
        self.assertFalse(is_leap_year(1900))
        self.assertFalse(is_leap_year(1979))


class FixOldLinksTestCase(TestCase):
    def test_topic(self):
        a = 'Hi <a href="http://www.pepysdiary.com/p/42.php">link</a> Bye'
        b = 'Hi <a href="http://www.pepysdiary.com/encyclopedia/42/">link</a> Bye'
        self.assertEqual(fix_old_links(a), b)

    def test_article(self):
        a = 'Hi <a href="http://www.pepysdiary.com/indepth/archive/2012/12/23/slug.php">link</a> Bye'  # noqa: E501
        b = 'Hi <a href="http://www.pepysdiary.com/indepth/2012/12/23/slug/">link</a> Bye'  # noqa: E501
        self.assertEqual(fix_old_links(a), b)

    def test_entry_1(self):
        a = 'Hi <a href="http://www.pepysdiary.com/archive/1666/12/23/">link</a> Bye'
        b = 'Hi <a href="http://www.pepysdiary.com/diary/1666/12/23/">link</a> Bye'
        self.assertEqual(fix_old_links(a), b)

    def test_entry_2(self):
        a = 'Hi <a href="http://www.pepysdiary.com/archive/1666/12/23/index.php">link</a> Bye'  # noqa: E501
        b = 'Hi <a href="http://www.pepysdiary.com/diary/1666/12/23/">link</a> Bye'
        self.assertEqual(fix_old_links(a), b)

    def test_letter(self):
        a = 'Hi <a href="http://www.pepysdiary.com/letters/1666/12/23/pepys-to-evelyn.php">link</a> Bye'  # noqa: E501
        b = 'Hi <a href="http://www.pepysdiary.com/letters/1666/12/23/pepys-to-evelyn/">link</a> Bye'  # noqa: E501
        self.assertEqual(fix_old_links(a), b)

    def test_article_image(self):
        a = 'Hi <a href="http://www.pepysdiary.com/indepth/images/2012/05/31/SamuelPepys_1666.jpg">link</a> Bye'  # noqa: E501
        b = 'Hi <a href="http://www.pepysdiary.com/static/img/indepth/2012/05/31/SamuelPepys_1666.jpg">link</a> Bye'  # noqa: E501
        self.assertEqual(fix_old_links(a), b)

    def test_about_image(self):
        a = 'Hi <a href="http://www.pepysdiary.com/about/archive/files/2012/05/31/SamuelPepys_1666.jpg">link</a> Bye'  # noqa: E501
        b = 'Hi <a href="http://www.pepysdiary.com/static/img/news/2012/05/31/SamuelPepys_1666.jpg">link</a> Bye'  # noqa: E501
        self.assertEqual(fix_old_links(a), b)

    def test_about_pdf(self):
        a = 'Hi <a href="http://www.pepysdiary.com/about/archive/files/2009/03/23/ParallelLivesFlyer2009.pdf">link</a> Bye'  # noqa: E501
        b = 'Hi <a href="http://www.pepysdiary.com/static/files/news/2009/03/23/ParallelLivesFlyer2009.pdf">link</a> Bye'  # noqa: E501
        self.assertEqual(fix_old_links(a), b)


class GetYearTestCase(TestCase):
    def test_get_year(self):
        d = make_date("1660-01-01")
        self.assertEqual(get_year(d), "1660")


class GetMonthTestCase(TestCase):
    def test_get_month(self):
        d = make_date("1660-01-01")
        self.assertEqual(get_month(d), "01")


class GetMonthBTestCase(TestCase):
    def test_get_month_b(self):
        d = make_date("1660-01-01")
        self.assertEqual(get_month_b(d), "Jan")


class GetDayTestCase(TestCase):
    def test_get_day(self):
        d = make_date("1660-01-01")
        self.assertEqual(get_day(d), "01")


class GetDayETestCase(TestCase):
    def test_get_day_e(self):
        d = make_date("1660-01-10")
        self.assertEqual(get_day_e(d), "10")

    def test_get_day_e_under_10(self):
        d = make_date("1660-01-01")
        self.assertEqual(get_day_e(d), "1")


class MakeURLAbsoluteTestCase(TestCase):
    def test_absolute(self):
        "Shouldn't change an already absolute URL"
        self.assertEqual(
            make_url_absolute("http://example.com/foo/bar/"),
            "http://example.com/foo/bar/",
        )

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_http(self):
        domain = Site.objects.get_current().domain
        self.assertEqual(
            make_url_absolute("/foo/bar/"),
            f"http://{domain}/foo/bar/",
        )

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_https(self):
        domain = Site.objects.get_current().domain
        self.assertEqual(
            make_url_absolute("/foo/bar/"),
            f"https://{domain}/foo/bar/",
        )
