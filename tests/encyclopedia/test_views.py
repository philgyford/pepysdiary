from unittest.mock import patch

from django.http.response import Http404

from pepysdiary.common.utilities import make_date
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia import views
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.encyclopedia.models import Category
from tests import ViewTestCase

DEFAULT_MAP_CATEGORY_ID = 28


class EncyclopediaViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.EncyclopediaView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.EncyclopediaView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "encyclopedia/category_list.html")

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


class CategoryMapViewTestCase(ViewTestCase):
    @patch("pepysdiary.encyclopedia.managers.CategoryManager.valid_map_category_ids")
    def test_response_200(self, mocked_valid_map_category_ids):
        "If category_id is in valid_map_category_ids and is a Category in the DB, 200"
        cat = Category.add_root()
        mocked_valid_map_category_ids.return_value = [cat.pk]

        response = views.CategoryMapView.as_view()(self.request, category_id=cat.pk)

        self.assertEqual(response.status_code, 200)

    def test_response_no_category_id(self):
        "If there's no category_id, it should raise a 404"
        with self.assertRaises(Http404):
            views.CategoryMapView.as_view()(self.request)

    def test_response_invalid_map_category_id(self):
        "If the category_id is not in the valid map categories, it should raise a 404"
        with self.assertRaises(Http404):
            views.CategoryMapView.as_view()(self.request, category_id=1)

    @patch("pepysdiary.encyclopedia.managers.CategoryManager.valid_map_category_ids")
    def test_response_category_does_not_exist(self, mocked_valid_map_category_ids):
        """If the category_id is in the valid map categories, but category does not exist
        it should raise a 404
        """
        cat = Category.add_root()
        # We'll look for this category_ID...
        wrong_cat_id = cat.pk + 1
        # ... which will be a valid_map_category_id:
        mocked_valid_map_category_ids.return_value = [wrong_cat_id]
        # but won't be a valid Category in the database.

        with self.assertRaises(Http404):
            views.CategoryMapView.as_view()(self.request, category_id=wrong_cat_id)

    @patch("pepysdiary.encyclopedia.managers.CategoryManager.valid_map_category_ids")
    def test_template(self, mocked_valid_map_category_ids):
        cat = Category.add_root()
        mocked_valid_map_category_ids.return_value = [cat.pk]

        response = views.CategoryMapView.as_view()(self.request, category_id=cat.pk)

        self.assertEqual(response.template_name[0], "encyclopedia/category_map.html")

    @patch("pepysdiary.encyclopedia.managers.CategoryManager.valid_map_category_ids")
    @patch("pepysdiary.encyclopedia.managers.TopicManager.pepys_homes_ids")
    def test_context_data(self, mocked_pepys_homes_ids, mocked_valid_map_category_ids):
        "It should contain all the correct category and topic context data"

        # 1. Create the Categories and Topics:

        cat_1 = Category.add_root()
        cat_2 = cat_1.add_child(title="Dogs")

        # A topic on cat_1 with lat/lon (should get passed to template):
        topic_1 = TopicFactory(
            title="Spaniels", categories=[cat_1], latitude=51, longitude=0
        )
        # A topic on cat_1 with no lat/lon
        TopicFactory(
            title="Retrievers", categories=[cat_1], latitude=None, longitude=None
        )
        # A topic on cat_2 with lat/lon:
        TopicFactory(title="Goldfish", categories=[cat_2], latitude=51, longitude=0)

        pepys_home_topic = TopicFactory()

        # 2. Mock a couple of methods to return IDs of the above:

        mocked_valid_map_category_ids.return_value = [cat_1.pk]
        mocked_pepys_homes_ids.return_value = [pepys_home_topic.pk]

        # 3. Call the view:

        response = views.CategoryMapView.as_view()(self.request, category_id=cat_1.pk)

        # 4. Test the context_data:

        data = response.context_data
        self.assertIn("category", data)
        self.assertEqual(data["category"], cat_1)

        self.assertIn("valid_map_category_ids", data)
        self.assertEqual(data["valid_map_category_ids"], [cat_1.pk])

        self.assertIn("pepys_homes_ids", data)
        self.assertEqual(data["pepys_homes_ids"], [pepys_home_topic.pk])

        # Topics should include our one Topic on cat_1, plus Pepys' home:
        self.assertIn("topics", data)
        self.assertEqual(len(data["topics"]), 2)
        self.assertEqual(data["topics"][0], topic_1)
        self.assertEqual(data["topics"][1], pepys_home_topic)

    def test_valid_form_submission(self):
        "Submitting the form successfully should redirect to the correct URL"
        # I couldn't successfully patch valid_map_category_ids() and
        # map_category_choices() for this test, for some reason, so just
        # using an ID from the actual valid list:
        ids = Category.objects.valid_map_category_ids()
        cat = Category.add_root(title="Animals", pk=ids[0])

        response = self.client.post("/encyclopedia/map/", {"category": str(cat.pk)})

        self.assertRedirects(response, f"/encyclopedia/map/{cat.pk}/")

    def test_invalid_form_submission(self):
        "If form is invalid it should display the page with an error"

        # Assuming that this is a Category ID that's not a valid choice:
        cat = Category.add_root(title="Animals", pk=99999)

        response = self.client.post("/encyclopedia/map/", {"category": str(cat.pk)})

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Select a valid choice. 99999 is not one of the available choices.",
            response.content.decode(),
        )
