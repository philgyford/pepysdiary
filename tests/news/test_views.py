from django.http.response import Http404

from pepysdiary.common.utilities import make_datetime
from pepysdiary.news import views
from pepysdiary.news.factories import DraftPostFactory, PublishedPostFactory
from pepysdiary.news.models import Post
from tests import ViewTestCase


class PostArchiveViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.PostArchiveView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.PostArchiveView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "news/post_list.html")

    def test_context_posts(self):
        "It should include the 10 most recent published Posts"
        PublishedPostFactory.create_batch(10)
        # One older published Post, shouldn't be included:
        old_post = PublishedPostFactory(
            date_published=make_datetime("2021-01-01 00:00:00")
        )
        # One draft Post, shouldn't be included:
        draft_post = DraftPostFactory()

        response = views.PostArchiveView.as_view()(self.request)

        data = response.context_data
        self.assertIn("object_list", data)
        self.assertIn("post_list", data)
        self.assertEqual(data["object_list"], data["post_list"])
        self.assertEqual(len(data["post_list"]), 10)
        self.assertNotIn(old_post, data["post_list"])
        self.assertNotIn(draft_post, data["post_list"])

    def test_context_categories(self):
        "It should include the categories in context"
        response = views.PostArchiveView.as_view()(self.request)
        data = response.context_data
        self.assertIn("categories", data)
        self.assertEqual(len(data["categories"]), len(Post.Category.choices))

    def test_pagination(self):
        PublishedPostFactory.create_batch(10)
        # Should be the only one on page 2:
        old_post = PublishedPostFactory(
            date_published=make_datetime("2021-01-01 00:00:00")
        )

        # Need to make a new request so we can pass the page argument in:
        request = self.factory.get("/fake-path/?page=2")
        response = views.PostArchiveView.as_view()(request)

        data = response.context_data
        self.assertIn("object_list", data)
        self.assertIn("post_list", data)
        self.assertEqual(len(data["post_list"]), 1)
        self.assertEqual(data["post_list"][0], old_post)


class PostCategoryArchiveViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.PostCategoryArchiveView.as_view()(
            self.request, category_slug="new-features"
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        with self.assertRaises(Http404):
            views.PostCategoryArchiveView.as_view()(self.request, category_slug="nope")

    def test_template(self):
        response = views.PostCategoryArchiveView.as_view()(
            self.request, category_slug="new-features"
        )
        self.assertEqual(response.template_name[0], "news/post_category_list.html")

    def test_context_data_posts(self):
        "It should include 10 published posts from this category"
        PublishedPostFactory.create_batch(
            11,
            category="new-features",
            date_published=make_datetime("2021-01-01 12:00:00"),
        )
        other_category_post = PublishedPostFactory(
            category="events", date_published=make_datetime("2021-01-02 12:00:00")
        )
        draft_post = DraftPostFactory(
            category="new-features", date_published=make_datetime("2021-01-02 12:00:00")
        )

        response = views.PostCategoryArchiveView.as_view()(
            self.request, category_slug="new-features"
        )
        data = response.context_data

        self.assertIn("object_list", data)
        self.assertIn("post_list", data)
        self.assertEqual(data["object_list"], data["post_list"])
        self.assertEqual(len(data["post_list"]), 10)
        self.assertNotIn(other_category_post, data["post_list"])
        self.assertNotIn(draft_post, data["post_list"])

    def test_context_data_category(self):
        "Context data should include the category info"
        response = views.PostCategoryArchiveView.as_view()(
            self.request, category_slug="new-features"
        )
        data = response.context_data
        self.assertIn("category_slug", data)
        self.assertEqual(data["category_slug"], "new-features")
        self.assertIn("category_name", data)
        self.assertEqual(data["category_name"], "New features")
        self.assertIn("categories", data)
        self.assertEqual(data["categories"], Post.Category.choices)


class PostDetailViewTestCase(ViewTestCase):
    def test_response_200(self):
        post = PublishedPostFactory(date_published=make_datetime("2021-01-02 12:00:00"))
        response = views.PostDetailView.as_view()(
            self.request, year="2021", month="01", day="02", pk=str(post.pk)
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        with self.assertRaises(Http404):
            views.PostDetailView.as_view()(
                self.request, year="2021", month="01", day="02", pk="123"
            )

    def test_template(self):
        post = PublishedPostFactory(date_published=make_datetime("2021-01-02 12:00:00"))
        response = views.PostDetailView.as_view()(
            self.request, year="2021", month="01", day="02", pk=str(post.pk)
        )
        self.assertEqual(response.template_name[0], "news/post_detail.html")

    def test_context_post(self):
        post = PublishedPostFactory(date_published=make_datetime("2021-01-02 12:00:00"))
        response = views.PostDetailView.as_view()(
            self.request, year="2021", month="01", day="02", pk=str(post.pk)
        )

        self.assertIn("post", response.context_data)
        self.assertEqual(response.context_data["post"], post)

    def test_context_next_previous(self):
        "If there are next/previous posts, they should be in the context"
        prev_post = PublishedPostFactory(
            date_published=make_datetime("2021-01-01 12:00:00")
        )
        post = PublishedPostFactory(date_published=make_datetime("2021-01-02 12:00:00"))
        next_post = PublishedPostFactory(
            date_published=make_datetime("2021-01-03 12:00:00")
        )

        response = views.PostDetailView.as_view()(
            self.request, year="2021", month="01", day="02", pk=str(post.pk)
        )

        self.assertIn("previous_post", response.context_data)
        self.assertEqual(response.context_data["previous_post"], prev_post)
        self.assertIn("next_post", response.context_data)
        self.assertEqual(response.context_data["next_post"], next_post)

    def test_context_no_next_previous(self):
        "If there's no next/previous, None should be in the context"
        post = PublishedPostFactory(date_published=make_datetime("2021-01-02 12:00:00"))

        response = views.PostDetailView.as_view()(
            self.request, year="2021", month="01", day="02", pk=str(post.pk)
        )

        self.assertIn("previous_post", response.context_data)
        self.assertIsNone(response.context_data["previous_post"])
        self.assertIn("next_post", response.context_data)
        self.assertIsNone(response.context_data["next_post"])
