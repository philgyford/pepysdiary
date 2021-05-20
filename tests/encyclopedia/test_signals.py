from django.test import TestCase

from pepysdiary.encyclopedia.factories import CategoryFactory, TopicFactory


class TopicCategoriesChangedTestCase(TestCase):
    def test_adding_category(self):
        "When we add a category to a topic, category's topic count should change"
        category = CategoryFactory()
        topic = TopicFactory()
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)

        topic.categories.add(category)
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

    def test_removing_category(self):
        "When we remove a category from a topic, category's topic count should change"
        category = CategoryFactory()
        topic = TopicFactory(categories=[category])
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

        topic.categories.remove(category)
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)
