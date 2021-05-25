from django.http.response import Http404

from pepysdiary.common.utilities import make_date
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia import views
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.encyclopedia.models import Category
from tests import ViewTestCase


class EncyclopediaViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.EncyclopediaView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.EncyclopediaView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "category_list.html")

    def test_context_data(self):
        cat_1 = Category.add_root(title="Animals")
        cat_2 = cat_1.add_child(title="Dogs")
        TopicFactory(categories=[cat_1])
        TopicFactory(categories=[cat_2])

        response = views.EncyclopediaView.as_view()(self.request)

        self.assertIn("categories", response.context_data)
        self.assertEqual(
            response.context_data["categories"],
            [
                (cat_1, {"open": True, "close": [], "level": 0}),
                (cat_2, {"open": True, "close": [0, 1], "level": 1}),
            ],
        )
        self.assertIn("topic_count", response.context_data)
        self.assertEqual(response.context_data["topic_count"], 2)


class CategoryDetailViewTestCase(ViewTestCase):
    def test_response_200(self):
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_1.add_child(title="Dogs", slug="dogs")
        response = views.CategoryDetailView.as_view()(
            self.request, slugs="animals/dogs"
        )
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_1.add_child(title="Dogs", slug="dogs")
        with self.assertRaises(Http404):
            views.CategoryDetailView.as_view()(self.request, slugs="animals/cats")

    def test_template(self):
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_1.add_child(title="Dogs", slug="dogs")
        response = views.CategoryDetailView.as_view()(
            self.request, slugs="animals/dogs"
        )
        self.assertEqual(response.template_name[0], "encyclopedia/category_detail.html")

    def test_no_slugs(self):
        "It should raise an AttributeError if no slugs argument is passed in."
        with self.assertRaises(AttributeError):
            views.CategoryDetailView.as_view()(self.request)

    def test_empty_slugs(self):
        "It should raise an Http404 if the slugs argument is empty."
        with self.assertRaises(Http404):
            views.CategoryDetailView.as_view()(self.request, slugs="")

    def test_context_data(self):
        cat_1 = Category.add_root(title="Animals", slug="animals")
        cat_2 = cat_1.add_child(title="Dogs", slug="dogs")
        cat_3 = cat_1.add_child(title="Fish", slug="fish")
        topic_1 = TopicFactory(title="Spaniels", categories=[cat_2])
        topic_2 = TopicFactory(title="Retrievers", categories=[cat_2])
        TopicFactory(title="Goldfish", categories=[cat_3])

        response = views.CategoryDetailView.as_view()(
            self.request, slugs="animals/dogs"
        )

        data = response.context_data

        self.assertIn("topics", data)
        self.assertEqual(len(data["topics"]), 2)
        self.assertIn(topic_1, data["topics"])
        self.assertIn(topic_2, data["topics"])

        self.assertIn("used_letters", data)
        self.assertEqual(data["used_letters"], ["R", "S"])

        self.assertIn("all_letters", data)
        self.assertEqual(
            data["all_letters"],
            [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
                "J",
                "K",
                "L",
                "M",
                "N",
                "O",
                "P",
                "Q",
                "R",
                "S",
                "T",
                "U",
                "V",
                "W",
                "X",
                "Y",
                "Z",
            ],
        )


class TopicDetailViewTestCase(ViewTestCase):
    def test_response_200(self):
        topic = TopicFactory()
        response = views.TopicDetailView.as_view()(self.request, pk=topic.pk)
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        topic = TopicFactory()
        with self.assertRaises(Http404):
            views.TopicDetailView.as_view()(self.request, pk=(topic.pk + 1))

    def test_template(self):
        topic = TopicFactory()
        response = views.TopicDetailView.as_view()(self.request, pk=topic.pk)
        self.assertEqual(response.template_name[0], "encyclopedia/topic_detail.html")

    def test_context_data(self):
        entry_1 = EntryFactory(diary_date=make_date("1661-01-01"))
        entry_2 = EntryFactory(diary_date=make_date("1661-02-01"))
        entry_3 = EntryFactory(diary_date=make_date("1662-03-04"))
        entry_4 = EntryFactory(diary_date=make_date("1662-03-05"))
        # Shouldn't be included:
        EntryFactory(diary_date=make_date("1663-01-01"))
        topic = TopicFactory(diary_references=[entry_1, entry_2, entry_3, entry_4])

        response = views.TopicDetailView.as_view()(self.request, pk=topic.pk)

        self.assertIn("diary_references", response.context_data)
        self.assertEqual(len(response.context_data["diary_references"]), 2)
        self.assertEqual(
            response.context_data["diary_references"],
            [
                ["1661", [["Jan", [entry_1]], ["Feb", [entry_2]]]],
                ["1662", [["Mar", [entry_3, entry_4]]]],
            ],
        )
