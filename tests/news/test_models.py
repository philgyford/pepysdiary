from django.test import TestCase
from django_comments.moderation import AlreadyModerated, moderator
from freezegun import freeze_time

from pepysdiary.common.utilities import make_datetime
from pepysdiary.news.factories import DraftPostFactory, PublishedPostFactory
from pepysdiary.news.models import Post, PostModerator


class PostTestCase(TestCase):
    def test_str(self):
        post = PublishedPostFactory(title="My Post")
        self.assertEqual(str(post), "My Post")

    def test_short_title(self):
        post = PublishedPostFactory(title="My Post")
        self.assertEqual(post.short_title, "My Post")

    def test_objects(self):
        "It should return published and unpublished posts"
        post_1 = PublishedPostFactory()
        post_2 = DraftPostFactory()

        posts = Post.objects.all()

        self.assertEqual(len(posts), 2)
        self.assertIn(post_1, posts)
        self.assertIn(post_2, posts)

    def test_published_posts(self):
        "It should only return published posts"
        post_1 = PublishedPostFactory()
        post_2 = PublishedPostFactory()
        DraftPostFactory()

        posts = Post.published_posts.all()

        self.assertEqual(len(posts), 2)
        self.assertIn(post_1, posts)
        self.assertIn(post_2, posts)

    def test_ordering(self):
        "It should return posts in reverse chronological order"
        post_1 = PublishedPostFactory(
            date_published=make_datetime("2021-01-02 00:00:00")
        )
        post_2 = PublishedPostFactory(
            date_published=make_datetime("2021-01-01 00:00:00")
        )
        post_3 = PublishedPostFactory(
            date_published=make_datetime("2021-01-03 00:00:00")
        )

        posts = Post.objects.all()

        self.assertEqual(posts[0], post_3)
        self.assertEqual(posts[1], post_1)
        self.assertEqual(posts[2], post_2)

    def test_make_intro_and_text_html(self):
        "On save the intro_html and text_html fields should be populated"
        post = PublishedPostFactory(intro="**Hello**", text="*Bye*")
        self.assertEqual(post.intro_html, "<p><strong>Hello</strong></p>")
        self.assertEqual(post.text_html, "<p><em>Bye</em></p>")

    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    def test_set_date_published_for_published(self):
        "An empty date_published should be set to now() on save for a published post"
        post = PublishedPostFactory(date_published=None)
        self.assertEqual(post.date_published, make_datetime("2021-04-10 12:00:00"))

    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    def test_set_date_published_for_draft(self):
        "An empty date_published should be left alone for a draft post"
        post = DraftPostFactory(date_published=None)
        self.assertIsNone(post.date_published)

    def test_get_absolute_url(self):
        post = PublishedPostFactory(date_published=make_datetime("2021-01-02 00:00:00"))

        self.assertEqual(post.get_absolute_url(), f"/news/2021/01/02/{post.pk}/")

    def test_category_title(self):
        post = PublishedPostFactory(category="new-features")
        self.assertEqual(post.category_title, "New features")

    def test_is_valid_category_slug(self):
        self.assertTrue(Post.is_valid_category_slug("new-features"))
        self.assertFalse(Post.is_valid_category_slug("nope"))

    def test_category_slug_to_name(self):
        self.assertTrue(Post.is_valid_category_slug("new-features"))
        self.assertFalse(Post.is_valid_category_slug("nope"))


class PostModeratorTestCase(TestCase):
    def test_it_is_registered(self):
        # Shouldn't be able to register it again:
        with self.assertRaises(AlreadyModerated):
            moderator.register(Post, PostModerator)
