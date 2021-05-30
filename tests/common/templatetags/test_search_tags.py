from django.test import TestCase

from pepysdiary.annotations.factories import ArticleAnnotationFactory
from pepysdiary.common.templatetags.search_tags import search_summary
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.indepth.factories import PublishedArticleFactory
from pepysdiary.news.factories import PublishedPostFactory
from pepysdiary.letters.factories import LetterFactory


class SearchSummaryTestCase(TestCase):

    def test_annotation(self):
        annotation = ArticleAnnotationFactory(
            comment=(
                "This is about cats. And some more text here which goes on for a "
                "while so that we can get a second mention of the animals "
                "in here. Cats are good."
            )
        )
        result = search_summary(annotation, "cats")
        self.assertEqual(
            result,
            (
                "This is about <b>cats</b>. And some more text here which goes on for "
                "a … he animals in here. <b>Cats</b> are good."
            ),
        )

    def test_article(self):
        article = PublishedArticleFactory(
            title="My title is about cats",
            intro="This is my Cats intro which goes on for a while here like this.",
            text="And this is my text which also mentions cats here.",
        )
        result = search_summary(article, "cats")
        self.assertEqual(
            result,
            (
                "My title is about <b>cats</b> This is my <b>Cats</b> intro which "
                "goes on for a while here like … which also mentions <b>cats</b> here."
            ),
        )

    def test_entry(self):
        entry = EntryFactory(
            text="This is my text about Cats which goes on.",
            footnotes="This is my footnotes text about cats.",
        )
        result = search_summary(entry, "cats")
        self.assertEqual(
            result,
            (
                "… is is my text about <b>Cats</b> which goes on. This is my footnotes "
                "text about <b>cats</b>."
            ),
        )

    def test_letter(self):
        letter = LetterFactory(
            title="My title is about cats",
            text="This is my Cats text which goes on for a while here like this.",
            footnotes="And this is my footnotes text which also mentions cats here.",
        )
        result = search_summary(letter, "cats")
        self.assertEqual(
            result,
            (
                "My title is about <b>cats</b> This is my <b>Cats</b> text which goes "
                "on for a while here like … which also mentions <b>cats</b> here."
            ),
        )

    def test_post(self):
        post = PublishedPostFactory(
            title="My title is about cats",
            intro="This is my Cats intro which goes on for a while here like this.",
            text="And this is my text which also mentions cats here.",
        )
        result = search_summary(post, "cats")
        self.assertEqual(
            result,
            (
                "My title is about <b>cats</b> This is my <b>Cats</b> intro which "
                "goes on for a while here like … which also mentions <b>cats</b> here."
            ),
        )

    def test_topic(self):
        post = TopicFactory(
            title="My title is about cats",
            summary="This is my Cats summary which goes on for a while here like this.",
            wheatley="And this is my Wheatley text which also mentions cats here.",
            wikipedia_html="<p>Finally, this is HTML about cats from Wikipedia.</p>",
        )
        result = search_summary(post, "cats")
        self.assertEqual(
            result,
            (
                "My title is about <b>cats</b> This is my <b>Cats</b> summary which "
                "goes on for a while here li … which also mentions <b>cats</b> here. "
                "Finally, this is HTML about <b>cats</b> from Wikipedia."
            ),
        )

    def test_strips_html(self):
        "It should strip all HTML"
        entry = EntryFactory(
            text="<p>This is my text<br> about Cats which goes on.</p>",
            footnotes="<p>This is my <em>footnotes</em> text about cats.</p>",
        )
        result = search_summary(entry, "cats")
        self.assertEqual(
            result,
            (
                "… is is my text about <b>Cats</b> which goes on. This is my "
                "footnotes text about <b>cats</b>."
            ),
        )

    def test_max_hilites_to_show(self):
        "It should only include max 10 mentions of the term with 'and more' on the end"
        entry = EntryFactory(
            text=(
                "One cats and some more text that goes on enough to split things up "
                "two cats and some more text that goes on enough to split things up "
                "three cats and some more text that goes on enough to split things up "
                "four cats and some more text that goes on enough to split things up "
                "five cats and some more text that goes on enough to split things up "
                "six cats and some more text that goes on enough to split things up "
                "seven cats and some more text that goes on enough to split things up "
                "eight cats and some more text that goes on enough to split things up "
                "nine cats and some more text that goes on enough to split things up "
                "ten cats and some more text that goes on enough to split things up "
                "eleven cats and some more text that goes on enough to split things up "
            )
        )
        result = search_summary(entry, "cats")
        self.assertEqual(
            result,
            (
                "One <b>cats</b> and some more text that goes on enough to split things … split things up two <b>cats</b> and some more text that goes on enough … lit things up three <b>cats</b> and some more text that goes on enough … plit things up four <b>cats</b> and some more text that goes on enough … plit things up five <b>cats</b> and some more text that goes on enough … split things up six <b>cats</b> and some more text that goes on enough … lit things up seven <b>cats</b> and some more text that goes on enough … lit things up eight <b>cats</b> and some more text that goes on enough … plit things up nine <b>cats</b> and some more text that goes on enough … split things up ten <b>cats</b> and some more text that goes on enough … <em>and 1 more.</em>"  # noqa: E501
            ),
        )
