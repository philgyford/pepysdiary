import os
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.request import QueryDict
from django.test import override_settings

from freezegun import freeze_time

from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.common import views
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.annotations.factories import EntryAnnotationFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
from pepysdiary.letters.factories import LetterFactory
from pepysdiary.news.factories import DraftPostFactory, PublishedPostFactory

from tests import ViewTestCase, ViewTransactionTestCase


# Location for files used in tests
ASSET_DIR = os.path.dirname(__file__) + "/../assets/"


class HomeViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.HomeView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.HomeView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "common/home.html")

    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    @override_settings(YEARS_OFFSET=353)
    def test_context_entry_list(self):
        "Context should include the 8 most recent published entries"
        # 9 published entries:
        for d in range(1, 10):
            EntryFactory(title=f"Entry {d}", diary_date=make_date(f"1668-04-0{d}"))

        # 1 unpublished entry:
        EntryFactory(diary_date=make_date("1668-04-10"))

        response = views.HomeView.as_view()(self.request)
        self.assertIn("entry_list", response.context_data)
        self.assertEqual(len(response.context_data["entry_list"]), 8)
        self.assertEqual(response.context_data["entry_list"][0].title, "Entry 9")
        self.assertEqual(response.context_data["entry_list"][7].title, "Entry 2")

    @freeze_time("2021-04-10 12:00:00", tz_offset=0)
    @override_settings(MEDIA_ROOT=tempfile.gettempdir(), YEARS_OFFSET=353)
    def test_context_tooltip_references(self):
        "The tooltip_references should contain the correct data"
        # 1 published entry:
        entry = EntryFactory(diary_date=make_date("1668-04-09"))

        # Need to use our test file to create the thumbnails:
        with open(
            os.path.join(ASSET_DIR, "topic_thumbnail.jpg"), "rb"
        ) as thumbnail_file:

            # 2 Topics referencing the Entry:
            topic_1 = TopicFactory(
                title="Cats",
                tooltip_text="About cats",
                thumbnail=SimpleUploadedFile("topic_1.jpg", thumbnail_file.read()),
            )
            topic_2 = TopicFactory(
                title="Dogs",
                tooltip_text="About dogs",
                thumbnail=SimpleUploadedFile("topic_2.jpg", thumbnail_file.read()),
            )

        topic_1.diary_references.add(entry)
        topic_2.diary_references.add(entry)

        response = views.HomeView.as_view()(self.request)
        self.assertIn("tooltip_references", response.context_data)
        self.assertEqual(len(response.context_data["tooltip_references"]), 2)

        # Now check the contents:
        # The image filenames have a random string on the end testing locally,
        # but not in GitHub Actions, so making it optional.
        refs = response.context_data["tooltip_references"]

        self.assertEqual(refs[str(topic_1.pk)]["title"], "Cats")
        self.assertEqual(refs[str(topic_1.pk)]["text"], "About cats")
        self.assertRegex(
            refs[str(topic_1.pk)]["thumbnail_url"],
            r"^/media/encyclopedia/thumbnails/topic_1",
        )

        self.assertEqual(refs[str(topic_2.pk)]["title"], "Dogs")
        self.assertEqual(refs[str(topic_2.pk)]["text"], "About dogs")
        self.assertRegex(
            refs[str(topic_2.pk)]["thumbnail_url"],
            r"^/media/encyclopedia/thumbnails/topic_2",
        )


class UpViewTestCase(ViewTestCase):
    def test_response_200(self):
        "It should respond with 200."
        response = views.up(self.request)
        self.assertEqual(response.status_code, 200)


class GoogleSearchViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.GoogleSearchView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.GoogleSearchView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "common/search_google.html")


class SearchViewTestCase(ViewTransactionTestCase):
    def test_response_200(self):
        response = views.SearchView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.SearchView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "common/search.html")

    def test_articles(self):
        "It should return matching published Articles"
        # These should appear in results:
        article_1 = PublishedArticleFactory(
            title="Cats",
            date_published=make_datetime("2020-01-01 12:00:00"),
        )
        article_2 = PublishedArticleFactory(
            title="More Cats",
            date_published=make_datetime("2020-01-02 12:00:00"),
        )

        # These should not appear in results:
        PublishedArticleFactory(title="Dogs")
        DraftArticleFactory(
            title="Draft Cats",
            date_published=make_datetime("2020-01-01 12:00:00"),
        )

        # Get Articles matching "cats" by relevancy:
        self.request.GET = QueryDict("k=a&q=cats&o=r")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(data["model_name"], "Article")
        self.assertEqual(data["search_string"], "cats")
        self.assertEqual(data["order_string"], "r")

        self.assertEqual(len(data["object_list"]), 2)
        self.assertIn(article_1, data["object_list"])
        self.assertIn(article_2, data["object_list"])

        self.assertEqual(data["object_list"], data["article_list"])

    def test_annotation(self):
        "It should return matching published Annotations"
        # These should appear in results:
        annotation_1 = EntryAnnotationFactory(
            comment="Cats",
            submit_date=make_datetime("2020-01-01 12:00:00"),
            is_public=True,
        )
        annotation_2 = EntryAnnotationFactory(
            comment="More Cats",
            submit_date=make_datetime("2020-01-02 12:00:00"),
            is_public=True,
        )

        # These should not appear in results:
        EntryAnnotationFactory(comment="Dogs", is_public=True)
        EntryAnnotationFactory(
            comment="Draft Cats",
            submit_date=make_datetime("2020-01-01 12:00:00"),
            is_public=False,
        )

        # Get Annotations matching "cats" by relevancy:
        self.request.GET = QueryDict("k=c&q=cats&o=r")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(data["model_name"], "Annotation")
        self.assertEqual(data["search_string"], "cats")
        self.assertEqual(data["order_string"], "r")

        self.assertEqual(len(data["object_list"]), 2)
        self.assertIn(annotation_1, data["object_list"])
        self.assertIn(annotation_2, data["object_list"])

        self.assertEqual(data["object_list"], data["annotation_list"])

    def test_letters(self):
        "It should return matching published Letters"
        # These should appear in results:
        letter_1 = LetterFactory(title="Cats")
        letter_2 = LetterFactory(title="More Cats")

        # This should not appear in results:
        LetterFactory(title="Dogs")

        # Get Letters matching "cats" by relevancy:
        self.request.GET = QueryDict("k=l&q=cats&o=r")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(data["model_name"], "Letter")
        self.assertEqual(data["search_string"], "cats")
        self.assertEqual(data["order_string"], "r")

        self.assertEqual(len(data["object_list"]), 2)
        self.assertIn(letter_1, data["object_list"])
        self.assertIn(letter_2, data["object_list"])

        self.assertEqual(data["object_list"], data["letter_list"])

    def test_posts(self):
        "It should return matching published Posts"
        # These should appear in results:
        post_1 = PublishedPostFactory(
            title="Cats",
            date_published=make_datetime("2020-01-01 12:00:00"),
        )
        post_2 = PublishedPostFactory(
            title="More Cats",
            date_published=make_datetime("2020-01-02 12:00:00"),
        )

        # These should not appear in results:
        PublishedPostFactory(title="Dogs")
        DraftPostFactory(
            title="Draft Cats",
            date_published=make_datetime("2020-01-01 12:00:00"),
        )

        # Get Posts matching "cats" by relevancy:
        self.request.GET = QueryDict("k=p&q=cats&o=r")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(data["model_name"], "Post")
        self.assertEqual(data["search_string"], "cats")
        self.assertEqual(data["order_string"], "r")

        self.assertEqual(len(data["object_list"]), 2)
        self.assertIn(post_1, data["object_list"])
        self.assertIn(post_2, data["object_list"])

        self.assertEqual(data["object_list"], data["post_list"])

    def test_topics(self):
        "It should return matching published Topics"
        # These should appear in results:
        topic_1 = TopicFactory(title="Cats")
        topic_2 = TopicFactory(title="More Cats")

        # This should not appear in results:
        TopicFactory(title="Dogs")

        # Get Posts matching "cats" by relevancy:
        self.request.GET = QueryDict("k=t&q=cats&o=r")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(data["model_name"], "Topic")
        self.assertEqual(data["search_string"], "cats")
        self.assertEqual(data["order_string"], "r")

        self.assertEqual(len(data["object_list"]), 2)
        self.assertIn(topic_1, data["object_list"])
        self.assertIn(topic_2, data["object_list"])

        self.assertEqual(data["object_list"], data["topic_list"])

    def test_entries(self):
        "It should return matching published Entries"
        # These should appear in results:
        entry_1 = EntryFactory(text="Cats")
        entry_2 = EntryFactory(text="More Cats")

        # This should not appear in results:
        EntryFactory(text="Dogs")

        # Get Posts matching "cats" by relevancy:
        self.request.GET = QueryDict("k=d&q=cats&o=r")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(data["model_name"], "Entry")
        self.assertEqual(data["search_string"], "cats")
        self.assertEqual(data["order_string"], "r")

        self.assertEqual(len(data["object_list"]), 2)
        self.assertIn(entry_1, data["object_list"])
        self.assertIn(entry_2, data["object_list"])

        self.assertEqual(data["object_list"], data["entry_list"])

    def test_ordering_rank(self):
        "It should order results by rank"
        entry_1 = EntryFactory(title="x", text="Cats", footnotes="x")
        entry_2 = EntryFactory(title="x", text="x", footnotes="Cats")
        entry_3 = EntryFactory(title="Cats", text="x", footnotes="x")

        # Order by relevance should be default:
        self.request.GET = QueryDict("q=cats")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(len(data["object_list"]), 3)
        self.assertEqual(data["object_list"][0], entry_3)
        self.assertEqual(data["object_list"][1], entry_1)
        self.assertEqual(data["object_list"][2], entry_2)

    def test_ordering_alphabetical(self):
        "It should order results by A-Z"
        entry_1 = EntryFactory(title="B Cats")
        entry_2 = EntryFactory(title="C Cats")
        entry_3 = EntryFactory(title="A Cats")

        # Sort by az:
        self.request.GET = QueryDict("q=cats&o=az")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(len(data["object_list"]), 3)
        self.assertEqual(data["object_list"][0], entry_3)
        self.assertEqual(data["object_list"][1], entry_1)
        self.assertEqual(data["object_list"][2], entry_2)

    def test_ordering_date_ascending(self):
        "It should order results by date ascending"
        entry_1 = EntryFactory(title="Cats", diary_date=make_date("1660-01-02"))
        entry_2 = EntryFactory(title="Cats", diary_date=make_date("1660-01-03"))
        entry_3 = EntryFactory(title="Cats", diary_date=make_date("1660-01-01"))

        # Sort by da:
        self.request.GET = QueryDict("q=cats&o=da")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(len(data["object_list"]), 3)
        self.assertEqual(data["object_list"][0], entry_3)
        self.assertEqual(data["object_list"][1], entry_1)
        self.assertEqual(data["object_list"][2], entry_2)

    def test_ordering_date_descending(self):
        "It should order results by date descending"
        entry_1 = EntryFactory(title="Cats", diary_date=make_date("1660-01-02"))
        entry_2 = EntryFactory(title="Cats", diary_date=make_date("1660-01-03"))
        entry_3 = EntryFactory(title="Cats", diary_date=make_date("1660-01-01"))

        # Sort by dd:
        self.request.GET = QueryDict("q=cats&o=dd")
        response = views.SearchView.as_view()(self.request)
        data = response.context_data

        self.assertEqual(len(data["object_list"]), 3)
        self.assertEqual(data["object_list"][0], entry_2)
        self.assertEqual(data["object_list"][1], entry_1)
        self.assertEqual(data["object_list"][2], entry_3)


class RecentViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.RecentView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.RecentView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "common/recent.html")


# No tests for the RedirectViews here because we fully test the URLs
# that they redirect in common/tests_urls.py.
