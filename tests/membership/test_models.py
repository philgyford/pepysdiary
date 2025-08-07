import time_machine
from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase, override_settings

from pepysdiary.common.utilities import make_datetime
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.indepth.factories import DraftArticleFactory, PublishedArticleFactory
from pepysdiary.membership.factories import PersonFactory
from pepysdiary.membership.models import Person


class PersonTestCase(TestCase):
    def test_str(self):
        person = PersonFactory(name="Bob Ferris")
        self.assertEqual(str(person), "Bob Ferris")

    def test_get_full_name(self):
        person = PersonFactory(name="Bob Ferris")
        self.assertEqual(person.get_full_name(), "Bob Ferris")

    def test_get_absolute_url(self):
        person = PersonFactory()
        self.assertEqual(person.get_absolute_url(), f"/account/profile/{person.pk}/")

    def test_topic_summaries(self):
        "It should have a reverse relationship to Topic"
        person = PersonFactory()
        topic_1 = TopicFactory(summary_author=person)
        topic_2 = TopicFactory(summary_author=person)
        # Shouldn't get included:
        TopicFactory()

        topics = person.topic_summaries.all()
        self.assertEqual(len(topics), 2)
        self.assertIn(topic_1, topics)
        self.assertIn(topic_2, topics)

    def test_get_summarised_topics(self):
        "It should return the person's topics, in alphabetical order"
        person = PersonFactory()
        topic_1 = TopicFactory(title="B", summary_author=person)
        topic_2 = TopicFactory(title="A", summary_author=person)

        topics = person.get_summarised_topics()
        self.assertEqual(len(topics), 2)
        self.assertEqual(topics[0], topic_2)
        self.assertEqual(topics[1], topic_1)

    def test_get_summarised_topics_none(self):
        "If the user has none, it should return an empty queryset"
        person = PersonFactory()
        topics = person.get_summarised_topics()
        self.assertEqual(len(topics), 0)

    def test_indepth_articles(self):
        "It should have a reverse relationship to Article"
        person = PersonFactory()
        article_1 = PublishedArticleFactory(author=person)
        article_2 = PublishedArticleFactory(author=person)
        article_3 = DraftArticleFactory(author=person)
        # Shouldn't get included:
        PublishedArticleFactory()

        articles = person.indepth_articles.all()
        self.assertEqual(len(articles), 3)
        self.assertIn(article_1, articles)
        self.assertIn(article_2, articles)
        self.assertIn(article_3, articles)

    def test_get_indepth_articles(self):
        "It should return the person's publishedArticles, in date order"
        person = PersonFactory()
        article_1 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), author=person
        )
        article_2 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-01 12:00:00"), author=person
        )
        # Shouldn't be included:
        DraftArticleFactory(author=person)

        articles = person.get_indepth_articles()
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0], article_2)
        self.assertEqual(articles[1], article_1)

    def test_get_indepth_articles_none(self):
        "If the user has none, it should return an empty queryset"
        person = PersonFactory()
        articles = person.get_indepth_articles()
        self.assertEqual(len(articles), 0)

    def test_activation_key_expired_true_already_activated(self):
        "If they're already activated, activation_key_expired should be true"
        person = PersonFactory(activation_key=Person.ACTIVATED)
        self.assertTrue(person.activation_key_expired())

    @override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    @time_machine.travel("2021-01-02 12:00:00 +0000", tick=False)
    def test_activation_key_expired_true_by_time(self):
        "If they've run out of time, activation_key_expired should be true"
        person = PersonFactory(activation_key="123456ABCDEF")
        person.date_created = make_datetime("2021-01-01 12:00:00")
        person.save()

        self.assertTrue(person.activation_key_expired())

    @override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    @time_machine.travel("2021-01-02 12:00:00 +0000", tick=False)
    def test_activation_key_expired_false(self):
        "If they haven't activated, and they're within the time limit, it's false"
        person = PersonFactory(activation_key="123456ABCDEF")
        person.date_created = make_datetime("2021-01-01 12:00:01")
        person.save()

        self.assertFalse(person.activation_key_expired())

    def test_send_activation_email(self):
        site = Site.objects.first()
        site.domain = "example.com"
        site.name = "Pepys' Diary"
        site.save()

        person = PersonFactory(activation_key="123456ABCDEF")
        person.send_activation_email(site)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Activate your Pepys' Diary account")
        self.assertIn(
            "https://example.com/account/activate/123456ABCDEF/", mail.outbox[0].body
        )
        self.assertDictEqual(
            mail.outbox[0].extra_headers,
            {
                "X-Auto-Response-Suppress": "OOF",
                "Auto-Submitted": "auto-generated",
            },
        )
