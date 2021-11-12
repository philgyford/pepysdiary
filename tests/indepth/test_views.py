from django.http.response import Http404

from pepysdiary.common.utilities import make_datetime
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
from pepysdiary.indepth.models import Article
from pepysdiary.indepth import views
from tests import ViewTestCase


class ArticleArchiveViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.ArticleArchiveView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.ArticleArchiveView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "indepth/article_list.html")

    def test_context_articles(self):
        "It should include the 10 most recent published Articles"
        PublishedArticleFactory.create_batch(10)
        # One older published Article, shouldn't be included:
        old_article = PublishedArticleFactory(
            date_published=make_datetime("2021-01-01 00:00:00")
        )
        # One draft Article, shouldn't be included:
        draft_article = DraftArticleFactory()

        response = views.ArticleArchiveView.as_view()(self.request)

        data = response.context_data
        self.assertIn("object_list", data)
        self.assertIn("article_list", data)
        self.assertEqual(data["object_list"], data["article_list"])
        self.assertEqual(len(data["article_list"]), 10)
        self.assertNotIn(old_article, data["article_list"])
        self.assertNotIn(draft_article, data["article_list"])

    def test_context_categories(self):
        "It should include the categories in context"
        response = views.ArticleArchiveView.as_view()(self.request)
        data = response.context_data
        self.assertIn("categories", data)
        self.assertEqual(len(data["categories"]), len(Article.Category.choices))

    def test_pagination(self):
        PublishedArticleFactory.create_batch(10)
        # Should be the only one on page 2:
        old_article = PublishedArticleFactory(
            date_published=make_datetime("2021-01-01 00:00:00")
        )

        # Need to make a new request so we can pass the page argument in:
        request = self.factory.get("/fake-path/?page=2")
        response = views.ArticleArchiveView.as_view()(request)

        data = response.context_data
        self.assertIn("object_list", data)
        self.assertIn("article_list", data)
        self.assertEqual(len(data["article_list"]), 1)
        self.assertEqual(data["article_list"][0], old_article)


class ArticleCategoryArchiveViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.ArticleCategoryArchiveView.as_view()(
            self.request, category_slug="book-reviews"
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        with self.assertRaises(Http404):
            views.ArticleCategoryArchiveView.as_view()(
                self.request, category_slug="nope"
            )

    def test_template(self):
        response = views.ArticleCategoryArchiveView.as_view()(
            self.request, category_slug="book-reviews"
        )
        self.assertEqual(
            response.template_name[0], "indepth/article_category_list.html"
        )

    def test_context_data_articles(self):
        "It should include 10 published articles from this category"
        PublishedArticleFactory.create_batch(
            11,
            category="book-reviews",
            date_published=make_datetime("2021-01-01 12:00:00"),
        )
        other_category_article = PublishedArticleFactory(
            category="events", date_published=make_datetime("2021-01-02 12:00:00")
        )
        draft_article = DraftArticleFactory(
            category="book-reviews", date_published=make_datetime("2021-01-02 12:00:00")
        )

        response = views.ArticleCategoryArchiveView.as_view()(
            self.request, category_slug="book-reviews"
        )
        data = response.context_data

        self.assertIn("object_list", data)
        self.assertIn("article_list", data)
        self.assertEqual(data["object_list"], data["article_list"])
        self.assertEqual(len(data["article_list"]), 10)
        self.assertNotIn(other_category_article, data["article_list"])
        self.assertNotIn(draft_article, data["article_list"])

    def test_context_data_category(self):
        "Context data should include the category info"
        response = views.ArticleCategoryArchiveView.as_view()(
            self.request, category_slug="book-reviews"
        )
        data = response.context_data
        self.assertIn("category_slug", data)
        self.assertEqual(data["category_slug"], "book-reviews")
        self.assertIn("category_name", data)
        self.assertEqual(data["category_name"], "Book Reviews")
        self.assertIn("categories", data)
        self.assertEqual(data["categories"], Article.Category.choices)


class ArticleDetailViewTestCase(ViewTestCase):
    def test_response_200(self):
        PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), slug="my-article"
        )
        response = views.ArticleDetailView.as_view()(
            self.request,
            year="2021",
            month="01",
            day="02",
            slug="my-article",
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        with self.assertRaises(Http404):
            views.ArticleDetailView.as_view()(
                self.request,
                year="2021",
                month="01",
                day="02",
                slug="my-article",
            )

    def test_template(self):
        PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), slug="my-article"
        )
        response = views.ArticleDetailView.as_view()(
            self.request,
            year="2021",
            month="01",
            day="02",
            slug="my-article",
        )
        self.assertEqual(response.template_name[0], "indepth/article_detail.html")

    def test_context_article(self):
        article = PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), slug="my-article"
        )
        response = views.ArticleDetailView.as_view()(
            self.request,
            year="2021",
            month="01",
            day="02",
            slug="my-article",
        )

        self.assertIn("article", response.context_data)
        self.assertEqual(response.context_data["article"], article)

    def test_context_next_previous(self):
        "If there are next/previous articles, they should be in the context"
        prev_article = PublishedArticleFactory(
            date_published=make_datetime("2021-01-01 12:00:00")
        )
        PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), slug="my-article"
        )
        next_article = PublishedArticleFactory(
            date_published=make_datetime("2021-01-03 12:00:00")
        )

        response = views.ArticleDetailView.as_view()(
            self.request,
            year="2021",
            month="01",
            day="02",
            slug="my-article",
        )

        self.assertIn("previous_article", response.context_data)
        self.assertEqual(response.context_data["previous_article"], prev_article)
        self.assertIn("next_article", response.context_data)
        self.assertEqual(response.context_data["next_article"], next_article)

    def test_context_no_next_previous(self):
        "If there's no next/previous, None should be in the context"
        PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), slug="my-article"
        )

        response = views.ArticleDetailView.as_view()(
            self.request,
            year="2021",
            month="01",
            day="02",
            slug="my-article",
        )

        self.assertIn("previous_article", response.context_data)
        self.assertIsNone(response.context_data["previous_article"])
        self.assertIn("next_article", response.context_data)
        self.assertIsNone(response.context_data["next_article"])
