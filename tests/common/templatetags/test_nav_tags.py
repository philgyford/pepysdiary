from django.test import TestCase

from pepysdiary.common.templatetags.nav_tags import get_subnav


class NavTagsTestCase(TestCase):

    def test_getsubnav_success(self):
        "It should return the correct subnav name for a URL name"
        # Just testing one per subnav section
        self.assertEqual(get_subnav("entry_detail"), "diary")
        self.assertEqual(get_subnav("letter_detail"), "letters")
        self.assertEqual(get_subnav("topic_detail"), "encyclopedia")
        self.assertEqual(get_subnav("article_detail"), "indepth")
        self.assertEqual(get_subnav("post_detail"), "news")
        self.assertEqual(get_subnav("recent"), "recent")
        self.assertEqual(get_subnav("about_text"), "about")

    def test_getsubnav_failure(self):
        "It should return False if it can't find the URL name"
        self.assertFalse(get_subnav("bibble"))
