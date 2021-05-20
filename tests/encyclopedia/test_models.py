from django.test import TestCase, TransactionTestCase

from pepysdiary.common.utilities import make_date
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia import category_lookups
from pepysdiary.encyclopedia.factories import (
    CategoryFactory,
    PersonTopicFactory,
    PlaceTopicFactory,
    TopicFactory,
)
from pepysdiary.encyclopedia.models import Category
from pepysdiary.letters.factories import LetterFactory


class CategoryTestCase(TestCase):
    def test_topics(self):
        cat = CategoryFactory(title="Animals")
        topic_1 = TopicFactory(categories=[cat])
        topic_2 = TopicFactory(categories=[cat])

        topics = cat.topics.all()

        self.assertEqual(len(topics), 2)
        self.assertIn(topic_1, topics)
        self.assertIn(topic_2, topics)

    def test_str(self):
        cat = CategoryFactory(title="Animals")
        self.assertEqual(str(cat), "Animals")

    def test_get_absolute_url_child(self):
        "It should generate the URL for a category with parents"
        cat_1 = Category.add_root(title="Aniamls", slug="animals")
        cat_2 = cat_1.add_child(title="Dogs", slug="dogs")
        cat_3 = cat_2.add_child(title="Terriers", slug="terriers")

        self.assertEqual(
            cat_3.get_absolute_url(), "/encyclopedia/animals/dogs/terriers/"
        )

    def test_get_absolute_url_parent(self):
        "It should generate the URL for a category with no parents"
        cat_1 = CategoryFactory(title="Animals", slug="animals")
        self.assertEqual(cat_1.get_absolute_url(), "/encyclopedia/animals/")


class TopicTestCase(TransactionTestCase):
    def test_categories(self):
        "Topic.categories should return the correct Categories"
        cat_1 = CategoryFactory(title="Animals")
        cat_2 = cat_1.add_child(title="Birds")
        topic = TopicFactory(categories=[cat_1, cat_2])

        categories = topic.categories.all()

        self.assertEqual(len(categories), 2)
        self.assertIn(cat_1, categories)
        self.assertIn(cat_2, categories)

    def test_diary_references(self):
        "Topic.diary_references should return the correct Entries"
        entry_1 = EntryFactory(diary_date=make_date("1661-01-01"))
        entry_2 = EntryFactory(diary_date=make_date("1661-01-02"))
        topic = TopicFactory(diary_references=[entry_1, entry_2])

        entries = topic.diary_references.all()

        self.assertEqual(len(entries), 2)
        self.assertIn(entry_1, entries)
        self.assertIn(entry_2, entries)

    def test_letter_references(self):
        "Topic.letter_references should return the correct Letters"
        letter_1 = LetterFactory(letter_date=make_date("1661-01-01"))
        letter_2 = LetterFactory(letter_date=make_date("1661-01-02"))
        topic = TopicFactory(letter_references=[letter_1, letter_2])

        letters = topic.letter_references.all()

        self.assertEqual(len(letters), 2)
        self.assertIn(letter_1, letters)
        self.assertIn(letter_2, letters)

    def test_str(self):
        topic = TopicFactory(title="Cats")
        self.assertEqual(str(topic), "Cats")

    def test_summary_html_is_created(self):
        topic = TopicFactory(summary="Hello.")
        self.assertEqual(topic.summary_html, "<p>Hello.</p>")

    def test_wheatley_html_is_created(self):
        topic = TopicFactory(wheatley="Hello.")
        self.assertEqual(topic.wheatley_html, "<p>Hello.</p>")

    def test_order_title_person(self):
        "On save order_title should be created correctly for people"
        topic = PersonTopicFactory(title="Bob Ferris", order_title="")
        self.assertEqual(topic.order_title, "Ferris, Bob")

    def test_order_title_not_person(self):
        "On save order_title should be created correctly for things that aren't people"
        topic = PlaceTopicFactory(title="The Cats", order_title="")
        self.assertEqual(topic.order_title, "Cats, The")

    def test_has_location_true(self):
        topic = TopicFactory(latitude=0, longitude=0)
        self.assertTrue(topic.has_location)

    def test_has_location_false(self):
        topic = TopicFactory(latitude=None, longitude=None)
        self.assertFalse(topic.has_location)

    def test_has_location_false_no_latitude(self):
        topic = TopicFactory(latitude=None, longitude=0)
        self.assertFalse(topic.has_location)

    def test_has_location_false_no_longitude(self):
        topic = TopicFactory(latitude=0, longitude=None)
        self.assertFalse(topic.has_location)

    def test_has_polygon_true(self):
        topic = TopicFactory(shape="0,0;1,0;1,1;1,0;0,0")
        self.assertTrue(topic.has_polygon)

    def test_has_polygon_false(self):
        topic = TopicFactory(shape="")
        self.assertFalse(topic.has_polygon)

    def test_has_polygon_false_not_complete(self):
        topic = TopicFactory(shape="0,0;1,0;1,1;1,0")
        self.assertFalse(topic.has_polygon)

    def test_has_path_true(self):
        topic = TopicFactory(shape="0,0;1,0;1,1;1,0")
        self.assertTrue(topic.has_path)

    def test_has_path_false(self):
        topic = TopicFactory(shape="")
        self.assertFalse(topic.has_path)

    def test_has_path_false_its_a_shape(self):
        topic = TopicFactory(shape="0,0;1,0;1,1;1,0;0,0")
        self.assertFalse(topic.has_path)

    def test_get_absolute_url(self):
        topic = TopicFactory(id=123)
        self.assertEqual(topic.get_absolute_url(), "/encyclopedia/123/")

    def test_get_annotated_diary_references(self):
        entry_1 = EntryFactory(diary_date=make_date("1661-01-01"))
        entry_2 = EntryFactory(diary_date=make_date("1661-02-01"))
        entry_3 = EntryFactory(diary_date=make_date("1662-03-04"))
        entry_4 = EntryFactory(diary_date=make_date("1662-03-05"))
        # Shouldn't be included:
        EntryFactory(diary_date=make_date("1663-01-01"))

        topic = TopicFactory(diary_references=[entry_1, entry_2, entry_3, entry_4])

        references = topic.get_annotated_diary_references()

        self.assertEqual(
            references,
            [
                ["1661", [["Jan", [entry_1]], ["Feb", [entry_2]]]],
                ["1662", [["Mar", [entry_3, entry_4]]]],
            ],
        )

    def test_get_annotated_diary_references_none(self):
        "It should return an empty list of there are no references"
        topic = TopicFactory()
        self.assertEqual(topic.get_annotated_diary_references(), [])

    def test_wikipedia_url(self):
        topic = TopicFactory(wikipedia_fragment="Samuel_Pepys")
        self.assertEqual(
            topic.wikipedia_url, "https://en.wikipedia.org/wiki/Samuel_Pepys"
        )

    def test_wikipedia_url_none(self):
        topic = TopicFactory(wikipedia_fragment="")
        self.assertEqual(topic.wikipedia_url, "")

    def test_category_map_id_exists(self):
        "It returns the Category's ID if it's a map category"
        category = CategoryFactory(id=category_lookups.PLACES_LONDON_STREETS)
        topic = TopicFactory(categories=[category])
        self.assertEqual(topic.category_map_id, category.id)

    def test_category_map_id_true(self):
        "It returns None if the Category isn't a map category"
        category = CategoryFactory(id=1)
        topic = TopicFactory(categories=[category])
        self.assertIsNone(topic.category_map_id)

    def test_is_family_tree_true(self):
        topic = TopicFactory(id=7390)
        self.assertTrue(topic.is_family_tree)

    def test_is_family_tree_false(self):
        topic = TopicFactory(id=123)
        self.assertFalse(topic.is_family_tree)

    def test_is_person_true(self):
        topic = PersonTopicFactory()
        self.assertTrue(topic.is_person)

    def test_is_person_false_no_categories(self):
        "Should return False if it has no categories"
        topic = TopicFactory()
        self.assertFalse(topic.is_person)

    def test_is_person_false_has_categories(self):
        "Should return False if it has categories, but none are People"
        topic = PlaceTopicFactory()
        self.assertFalse(topic.is_person)

    def test_is_place_true(self):
        topic = PlaceTopicFactory()
        self.assertTrue(topic.is_place)

    def test_is_place_false_no_categories(self):
        "Should return False if it has no categories"
        topic = TopicFactory()
        self.assertFalse(topic.is_place)

    def test_is_place_false_has_categories(self):
        "Should return False if it has categories, but none are Places"
        topic = PersonTopicFactory()
        self.assertFalse(topic.is_place)
