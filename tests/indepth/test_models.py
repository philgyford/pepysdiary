from django.test import TestCase
from django_comments.moderation import AlreadyModerated, moderator
from freezegun import freeze_time

from pepysdiary.common.utilities import make_datetime
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
from pepysdiary.indepth.models import Article, ArticleModerator


class ArticleTestCase(TestCase):
    def test_str(self):
        article = PublishedArticleFactory(title="My Article")
        self.assertEqual(str(article), "My Article")

    def test_short_title(self):
        article = PublishedArticleFactory(title="My Article")
        self.assertEqual(article.short_title, "My Article")

    def test_objects(self):
        "It should return published and unpublished articles"
        article_1 = PublishedArticleFactory()
        article_2 = DraftArticleFactory()

        articles = Article.objects.all()

        self.assertEqual(len(articles), 2)
        self.assertIn(article_1, articles)
        self.assertIn(article_2, articles)

    def test_published_articles(self):
        "It should only return published articles"
        article_1 = PublishedArticleFactory()
        article_2 = PublishedArticleFactory()
        DraftArticleFactory()

        articles = Article.published_articles.all()

        self.assertEqual(len(articles), 2)
        self.assertIn(article_1, articles)
        self.assertIn(article_2, articles)

    def test_ordering(self):
        "It should return articles in reverse chronological order"
        article_1 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 00:00:00")
        )
        article_2 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-01 00:00:00")
        )
        article_3 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-03 00:00:00")
        )

        articles = Article.objects.all()

        self.assertEqual(articles[0], article_3)
        self.assertEqual(articles[1], article_1)
        self.assertEqual(articles[2], article_2)

    def test_make_intro_and_text_html(self):
        "On save the intro_html and text_html fields should be populated"
        article = PublishedArticleFactory(intro="**Hello**", text="*Bye*")
        self.assertEqual(article.intro_html, "<p><strong>Hello</strong></p>")
        self.assertEqual(article.text_html, "<p><em>Bye</em></p>")

    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    def test_set_date_published_for_published(self):
        "An empty date_published should be set to now() on save for a published article"
        article = PublishedArticleFactory(date_published=None)
        self.assertEqual(article.date_published, make_datetime("2021-04-10 12:00:00"))

    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    def test_set_date_published_for_draft(self):
        "An empty date_published should be left alone for a draft article"
        article = DraftArticleFactory(date_published=None)
        self.assertIsNone(article.date_published)

    def test_get_absolute_url(self):
        article = PublishedArticleFactory.build(
            date_published=make_datetime("2021-01-02 00:00:00"), slug="my-article"
        )

        self.assertEqual(article.get_absolute_url(), "/indepth/2021/01/02/my-article/")

    def test_category_title(self):
        article = PublishedArticleFactory(category="book-reviews")
        self.assertEqual(article.category_title, "Book Reviews")

    def test_is_valid_category_slug(self):
        self.assertTrue(Article.is_valid_category_slug("book-reviews"))
        self.assertFalse(Article.is_valid_category_slug("nope"))

    def test_category_slug_to_name(self):
        self.assertEqual(Article.category_slug_to_name("book-reviews"), "Book Reviews")
        self.assertEqual(Article.category_slug_to_name("nope"), "")


class ArticleModeratorTestCase(TestCase):
    def test_it_is_registered(self):
        # Shouldn't be able to register it again:
        with self.assertRaises(AlreadyModerated):
            moderator.register(Article, ArticleModerator)
