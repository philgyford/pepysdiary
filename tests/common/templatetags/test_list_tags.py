from django.test import TestCase

from pepysdiary.common.templatetags.list_tags import (
    latest_commented_articles,
    latest_commented_entries,
    latest_commented_letters,
    latest_commented_posts,
    latest_commented_topics,
)
from pepysdiary.common.utilities import make_datetime
from pepysdiary.annotations.factories import (
    ArticleAnnotationFactory,
    EntryAnnotationFactory,
    LetterAnnotationFactory,
    PostAnnotationFactory,
    TopicAnnotationFactory,
)
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.indepth.factories import PublishedArticleFactory
from pepysdiary.news.factories import PublishedPostFactory
from pepysdiary.letters.factories import LetterFactory


class ListTagsTestCase(TestCase):
    def test_latest_commented_entries(self):
        entry_1 = EntryFactory(diary_date=make_date("1660-01-01"))
        entry_2 = EntryFactory(diary_date=make_date("1660-01-02"))
        entry_3 = EntryFactory(diary_date=make_date("1660-01-03"))
        entry_4 = EntryFactory(diary_date=make_date("1660-01-04"))

        annotation_1 = EntryAnnotationFactory(
            user_name="Name 1",
            content_object=entry_1,
            submit_date=make_datetime("2021-04-09 01:00:00"),
        )
        annotation_2 = EntryAnnotationFactory(
            user_name="Name 2",
            content_object=entry_2,
            submit_date=make_datetime("2021-04-10 01:00:00"),
        )
        annotation_3 = EntryAnnotationFactory(
            user_name="Name 3",
            content_object=entry_3,
            submit_date=make_datetime("2021-04-08 01:00:00"),
        )
        EntryAnnotationFactory(
            content_object=entry_4, submit_date=make_datetime("2021-04-07 01:00:00")
        )

        result = latest_commented_entries({}, "Test Title", quantity=3)

        self.assertIn("title", result)
        self.assertEqual(result["title"], "Test Title")

        self.assertIn("comments", result)
        self.assertEqual(len(result["comments"]), 3)

        item_0 = result["comments"][0]
        self.assertEqual(item_0["data_time"], 1618016400)
        self.assertEqual(item_0["date"], "10 Apr 2021")
        self.assertEqual(item_0["iso_datetime"], "2021-04-10T01:00:00+0000")
        self.assertEqual(item_0["obj_title"], entry_2.title)
        self.assertIn(annotation_2.comment[:50], item_0["text"])
        self.assertEqual(item_0["time"], "1:00am")
        self.assertEqual(item_0["user_name"], "Name 2")

        item_1 = result["comments"][1]
        self.assertEqual(item_1["data_time"], 1617930000)
        self.assertEqual(item_1["date"], "9 Apr 2021")
        self.assertEqual(item_1["iso_datetime"], "2021-04-09T01:00:00+0000")
        self.assertEqual(item_1["obj_title"], entry_1.title)
        self.assertIn(annotation_1.comment[:50], item_1["text"])
        self.assertEqual(item_1["time"], "1:00am")
        self.assertEqual(item_1["user_name"], "Name 1")

        item_2 = result["comments"][2]
        self.assertEqual(item_2["data_time"], 1617843600)
        self.assertEqual(item_2["date"], "8 Apr 2021")
        self.assertEqual(item_2["iso_datetime"], "2021-04-08T01:00:00+0000")
        self.assertEqual(item_2["obj_title"], entry_3.title)
        self.assertIn(annotation_3.comment[:50], item_2["text"])
        self.assertEqual(item_2["time"], "1:00am")
        self.assertEqual(item_2["user_name"], "Name 3")

    def test_latest_commented_letters(self):
        letter_1 = LetterFactory()
        letter_2 = LetterFactory()
        letter_3 = LetterFactory()
        letter_4 = LetterFactory()

        annotation_1 = LetterAnnotationFactory(
            user_name="Name 1",
            content_object=letter_1,
            submit_date=make_datetime("2021-04-09 01:00:00"),
        )
        annotation_2 = LetterAnnotationFactory(
            user_name="Name 2",
            content_object=letter_2,
            submit_date=make_datetime("2021-04-10 01:00:00"),
        )
        annotation_3 = LetterAnnotationFactory(
            user_name="Name 3",
            content_object=letter_3,
            submit_date=make_datetime("2021-04-08 01:00:00"),
        )
        LetterAnnotationFactory(
            content_object=letter_4, submit_date=make_datetime("2021-04-07 01:00:00")
        )

        result = latest_commented_letters({}, "Test Title", quantity=3)

        self.assertIn("title", result)
        self.assertEqual(result["title"], "Test Title")

        self.assertIn("comments", result)
        self.assertEqual(len(result["comments"]), 3)

        item_0 = result["comments"][0]
        self.assertEqual(item_0["data_time"], 1618016400)
        self.assertEqual(item_0["date"], "10 Apr 2021")
        self.assertEqual(item_0["iso_datetime"], "2021-04-10T01:00:00+0000")
        self.assertEqual(item_0["obj_title"], letter_2.title)
        self.assertIn(annotation_2.comment[:50], item_0["text"])
        self.assertEqual(item_0["time"], "1:00am")
        self.assertEqual(item_0["user_name"], "Name 2")

        item_1 = result["comments"][1]
        self.assertEqual(item_1["data_time"], 1617930000)
        self.assertEqual(item_1["date"], "9 Apr 2021")
        self.assertEqual(item_1["iso_datetime"], "2021-04-09T01:00:00+0000")
        self.assertEqual(item_1["obj_title"], letter_1.title)
        self.assertIn(annotation_1.comment[:50], item_1["text"])
        self.assertEqual(item_1["time"], "1:00am")
        self.assertEqual(item_1["user_name"], "Name 1")

        item_2 = result["comments"][2]
        self.assertEqual(item_2["data_time"], 1617843600)
        self.assertEqual(item_2["date"], "8 Apr 2021")
        self.assertEqual(item_2["iso_datetime"], "2021-04-08T01:00:00+0000")
        self.assertEqual(item_2["obj_title"], letter_3.title)
        self.assertIn(annotation_3.comment[:50], item_2["text"])
        self.assertEqual(item_2["time"], "1:00am")
        self.assertEqual(item_2["user_name"], "Name 3")

    def test_latest_commented_topics(self):
        topic_1 = TopicFactory()
        topic_2 = TopicFactory()
        topic_3 = TopicFactory()
        topic_4 = TopicFactory()

        annotation_1 = TopicAnnotationFactory(
            user_name="Name 1",
            content_object=topic_1,
            submit_date=make_datetime("2021-04-09 01:00:00"),
        )
        annotation_2 = TopicAnnotationFactory(
            user_name="Name 2",
            content_object=topic_2,
            submit_date=make_datetime("2021-04-10 01:00:00"),
        )
        annotation_3 = TopicAnnotationFactory(
            user_name="Name 3",
            content_object=topic_3,
            submit_date=make_datetime("2021-04-08 01:00:00"),
        )
        TopicAnnotationFactory(
            content_object=topic_4, submit_date=make_datetime("2021-04-07 01:00:00")
        )

        result = latest_commented_topics({}, "Test Title", quantity=3)

        self.assertIn("title", result)
        self.assertEqual(result["title"], "Test Title")

        self.assertIn("comments", result)
        self.assertEqual(len(result["comments"]), 3)

        item_0 = result["comments"][0]
        self.assertEqual(item_0["data_time"], 1618016400)
        self.assertEqual(item_0["date"], "10 Apr 2021")
        self.assertEqual(item_0["iso_datetime"], "2021-04-10T01:00:00+0000")
        self.assertEqual(item_0["obj_title"], topic_2.title)
        self.assertIn(annotation_2.comment[:50], item_0["text"])
        self.assertEqual(item_0["time"], "1:00am")
        self.assertEqual(item_0["user_name"], "Name 2")

        item_1 = result["comments"][1]
        self.assertEqual(item_1["data_time"], 1617930000)
        self.assertEqual(item_1["date"], "9 Apr 2021")
        self.assertEqual(item_1["iso_datetime"], "2021-04-09T01:00:00+0000")
        self.assertEqual(item_1["obj_title"], topic_1.title)
        self.assertIn(annotation_1.comment[:50], item_1["text"])
        self.assertEqual(item_1["time"], "1:00am")
        self.assertEqual(item_1["user_name"], "Name 1")

        item_2 = result["comments"][2]
        self.assertEqual(item_2["data_time"], 1617843600)
        self.assertEqual(item_2["date"], "8 Apr 2021")
        self.assertEqual(item_2["iso_datetime"], "2021-04-08T01:00:00+0000")
        self.assertEqual(item_2["obj_title"], topic_3.title)
        self.assertIn(annotation_3.comment[:50], item_2["text"])
        self.assertEqual(item_2["time"], "1:00am")
        self.assertEqual(item_2["user_name"], "Name 3")

    def test_latest_commented_articles(self):
        article_1 = PublishedArticleFactory()
        article_2 = PublishedArticleFactory()
        article_3 = PublishedArticleFactory()
        article_4 = PublishedArticleFactory()

        annotation_1 = ArticleAnnotationFactory(
            user_name="Name 1",
            content_object=article_1,
            submit_date=make_datetime("2021-04-09 01:00:00"),
        )
        annotation_2 = ArticleAnnotationFactory(
            user_name="Name 2",
            content_object=article_2,
            submit_date=make_datetime("2021-04-10 01:00:00"),
        )
        annotation_3 = ArticleAnnotationFactory(
            user_name="Name 3",
            content_object=article_3,
            submit_date=make_datetime("2021-04-08 01:00:00"),
        )
        ArticleAnnotationFactory(
            content_object=article_4, submit_date=make_datetime("2021-04-07 01:00:00")
        )

        result = latest_commented_articles({}, "Test Title", quantity=3)

        self.assertIn("title", result)
        self.assertEqual(result["title"], "Test Title")

        self.assertIn("comments", result)
        self.assertEqual(len(result["comments"]), 3)

        item_0 = result["comments"][0]
        self.assertEqual(item_0["data_time"], 1618016400)
        self.assertEqual(item_0["date"], "10 Apr 2021")
        self.assertEqual(item_0["iso_datetime"], "2021-04-10T01:00:00+0000")
        self.assertEqual(item_0["obj_title"], article_2.title)
        self.assertIn(annotation_2.comment[:50], item_0["text"])
        self.assertEqual(item_0["time"], "1:00am")
        self.assertEqual(item_0["user_name"], "Name 2")

        item_1 = result["comments"][1]
        self.assertEqual(item_1["data_time"], 1617930000)
        self.assertEqual(item_1["date"], "9 Apr 2021")
        self.assertEqual(item_1["iso_datetime"], "2021-04-09T01:00:00+0000")
        self.assertEqual(item_1["obj_title"], article_1.title)
        self.assertIn(annotation_1.comment[:50], item_1["text"])
        self.assertEqual(item_1["time"], "1:00am")
        self.assertEqual(item_1["user_name"], "Name 1")

        item_2 = result["comments"][2]
        self.assertEqual(item_2["data_time"], 1617843600)
        self.assertEqual(item_2["date"], "8 Apr 2021")
        self.assertEqual(item_2["iso_datetime"], "2021-04-08T01:00:00+0000")
        self.assertEqual(item_2["obj_title"], article_3.title)
        self.assertIn(annotation_3.comment[:50], item_2["text"])
        self.assertEqual(item_2["time"], "1:00am")
        self.assertEqual(item_2["user_name"], "Name 3")

    def test_latest_commented_posts(self):
        post_1 = PublishedPostFactory()
        post_2 = PublishedPostFactory()
        post_3 = PublishedPostFactory()
        post_4 = PublishedPostFactory()

        annotation_1 = PostAnnotationFactory(
            user_name="Name 1",
            content_object=post_1,
            submit_date=make_datetime("2021-04-09 01:00:00"),
        )
        annotation_2 = PostAnnotationFactory(
            user_name="Name 2",
            content_object=post_2,
            submit_date=make_datetime("2021-04-10 01:00:00"),
        )
        annotation_3 = PostAnnotationFactory(
            user_name="Name 3",
            content_object=post_3,
            submit_date=make_datetime("2021-04-08 01:00:00"),
        )
        PostAnnotationFactory(
            content_object=post_4, submit_date=make_datetime("2021-04-07 01:00:00")
        )

        result = latest_commented_posts({}, "Test Title", quantity=3)

        self.assertIn("title", result)
        self.assertEqual(result["title"], "Test Title")

        self.assertIn("comments", result)
        self.assertEqual(len(result["comments"]), 3)

        item_0 = result["comments"][0]
        self.assertEqual(item_0["data_time"], 1618016400)
        self.assertEqual(item_0["date"], "10 Apr 2021")
        self.assertEqual(item_0["iso_datetime"], "2021-04-10T01:00:00+0000")
        self.assertEqual(item_0["obj_title"], post_2.title)
        self.assertIn(annotation_2.comment[:50], item_0["text"])
        self.assertEqual(item_0["time"], "1:00am")
        self.assertEqual(item_0["user_name"], "Name 2")

        item_1 = result["comments"][1]
        self.assertEqual(item_1["data_time"], 1617930000)
        self.assertEqual(item_1["date"], "9 Apr 2021")
        self.assertEqual(item_1["iso_datetime"], "2021-04-09T01:00:00+0000")
        self.assertEqual(item_1["obj_title"], post_1.title)
        self.assertIn(annotation_1.comment[:50], item_1["text"])
        self.assertEqual(item_1["time"], "1:00am")
        self.assertEqual(item_1["user_name"], "Name 1")

        item_2 = result["comments"][2]
        self.assertEqual(item_2["data_time"], 1617843600)
        self.assertEqual(item_2["date"], "8 Apr 2021")
        self.assertEqual(item_2["iso_datetime"], "2021-04-08T01:00:00+0000")
        self.assertEqual(item_2["obj_title"], post_3.title)
        self.assertIn(annotation_3.comment[:50], item_2["text"])
        self.assertEqual(item_2["time"], "1:00am")
        self.assertEqual(item_2["user_name"], "Name 3")

    def test_result_date_time_formats(self):
        "If the date and time formats are provided in the context, they should be used"
        entry_1 = EntryFactory()

        EntryAnnotationFactory(
            user_name="Name 1",
            content_object=entry_1,
            submit_date=make_datetime("2021-04-09 13:00:00"),
        )

        context = {
            "date_format_mid_strftime": "%Y%m%d",
            "time_format_strftime": "%H%M",
        }
        result = latest_commented_entries(context, "Test Title")

        self.assertEqual(result["comments"][0]["date"], "20210409")
        self.assertEqual(result["comments"][0]["time"], "1300")

    def test_no_results(self):
        "If there are no commented items it should return None"
        self.assertIsNone(latest_commented_entries({}, "Title"))
