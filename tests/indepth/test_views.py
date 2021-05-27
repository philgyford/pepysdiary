from pepysdiary.common.utilities import make_datetime
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
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
