# coding: utf-8
from pepysdiary.common.tests.test_base import PepysdiaryTestCase

from pepysdiary.encyclopedia.factories import CategoryFactory,\
        PersonTopicFactory, PlaceTopicFactory, TopicFactory 

# Only testing a handful of things at the moment.


class TopicTestCase(PepysdiaryTestCase):

    def test_is_family_tree_true(self):
        topic = TopicFactory(id=7390)
        self.assertTrue(topic.is_family_tree)

    def test_is_family_tree_false(self):
        topic = TopicFactory(id=123)
        self.assertFalse(topic.is_family_tree)

    def test_is_person_true(self):
        topic = PersonTopicFactory()
        self.assertTrue(topic.is_person)

    def test_is_person_false(self):
        topic = TopicFactory()
        self.assertFalse(topic.is_person)

    def test_is_place_true(self):
        topic = PlaceTopicFactory()
        self.assertTrue(topic.is_place)

    def test_is_place_false(self):
        topic = TopicFactory()
        self.assertFalse(topic.is_person)


