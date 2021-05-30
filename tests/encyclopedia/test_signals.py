from django.test import TestCase

from pepysdiary.encyclopedia.factories import CategoryFactory, TopicFactory


class TopicCategoriesChangedTestCase(TestCase):
    def test_adding_category_to_topic(self):
        "When we add a category to a topic, category's topic count should change"
        category = CategoryFactory()
        topic = TopicFactory()
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)

        topic.categories.add(category)
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

    def test_removing_category_from_topic(self):
        "When we remove a category from a topic, category's topic count should change"
        category = CategoryFactory()
        topic = TopicFactory(categories=[category])
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

        topic.categories.remove(category)
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)

    def test_adding_topic_to_category(self):
        "When we add a new topic to a category, category's topic count should change"
        category = CategoryFactory()
        topic = TopicFactory()
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)

        category.topics.add(topic)
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

    def test_removing_topic_from_category(self):
        "When we remove a topic from a category, category's topic count should change"
        category = CategoryFactory()
        topic = TopicFactory(categories=[category])
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

        category.topics.remove(topic)
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)

    def test_deleting_topic(self):
        "When we delete a topic its categories' topic counts should change"
        category = CategoryFactory()
        topic = TopicFactory(categories=[category])
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 1)

        topic.delete()
        category.refresh_from_db()
        self.assertEqual(category.topic_count, 0)
