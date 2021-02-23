from django.test import TestCase

from pepysdiary.common.utilities import hilite_words, trim_hilites


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
