from django.contrib.sites.models import Site
from django.test import TestCase

from pepysdiary.common.utilities import make_date, make_datetime
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.encyclopedia.models import Category
from pepysdiary.indepth.factories import PublishedArticleFactory
from pepysdiary.letters.factories import LetterFactory
from pepysdiary.news.factories import PublishedPostFactory
from pepysdiary.news.models import Post


class SitemapsTestCase(TestCase):
    def setUp(self):
        # Because otherwise, for some reason, the tests have a different domain,
        # and we need that to test URLs:
        site = Site.objects.first()
        site.domain = "example.com"
        site.save()

    def test_overall_sitemap_response(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)

    def test_overall_sitemap_content(self):
        response = self.client.get("/sitemap.xml")
        response_content = response.content.decode()
        self.assertIn(
            "<loc>http://example.com/sitemap-main.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-entries.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-letters.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-topics.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-articles.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-posts.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-archives.xml</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/sitemap-flatpages.xml</loc>", response_content
        )

    def test_static_sitemap_response(self):
        response = self.client.get("/sitemap-main.xml")
        self.assertEqual(response.status_code, 200)

    def test_static_sitemap_content(self):
        response = self.client.get("/sitemap-main.xml")
        response_content = response.content.decode()
        self.assertIn("<loc>http://example.com/</loc>", response_content)
        self.assertIn("<loc>http://example.com/recent/</loc>", response_content)
        self.assertIn("<loc>http://example.com/letters/</loc>", response_content)
        self.assertIn("<loc>http://example.com/encyclopedia/</loc>", response_content)
        self.assertIn("<loc>http://example.com/indepth/</loc>", response_content)
        self.assertIn("<loc>http://example.com/news/</loc>", response_content)

    def test_entry_sitemap_response(self):
        response = self.client.get("/sitemap-entries.xml")
        self.assertEqual(response.status_code, 200)

    def test_entry_sitemap_content(self):
        entry_1 = EntryFactory(diary_date=make_date("1660-01-01"))
        entry_2 = EntryFactory(diary_date=make_date("1660-01-02"))
        entry_3 = EntryFactory(diary_date=make_date("1660-01-03"))

        response = self.client.get("/sitemap-entries.xml")
        response_content = response.content.decode()
        self.assertIn(
            (
                "<loc>http://example.com/diary/1660/01/01/</loc>"
                f"<lastmod>{entry_1.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                "<loc>http://example.com/diary/1660/01/02/</loc>"
                f"<lastmod>{entry_2.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                "<loc>http://example.com/diary/1660/01/03/</loc>"
                f"<lastmod>{entry_3.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )

    def test_letter_sitemap_response(self):
        response = self.client.get("/sitemap-letters.xml")
        self.assertEqual(response.status_code, 200)

    def test_letter_sitemap_content(self):
        letter_1 = LetterFactory(letter_date=make_date("1660-01-01"), slug="letter1")
        letter_2 = LetterFactory(letter_date=make_date("1660-01-02"), slug="letter2")
        letter_3 = LetterFactory(letter_date=make_date("1660-01-03"), slug="letter3")

        response = self.client.get("/sitemap-letters.xml")
        response_content = response.content.decode()
        self.assertIn(
            (
                "<loc>http://example.com/letters/1660/01/01/letter1/</loc>"
                f"<lastmod>{letter_1.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                "<loc>http://example.com/letters/1660/01/02/letter2/</loc>"
                f"<lastmod>{letter_2.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                "<loc>http://example.com/letters/1660/01/03/letter3/</loc>"
                f"<lastmod>{letter_3.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )

    def test_topic_sitemap_response(self):
        response = self.client.get("/sitemap-topics.xml")
        self.assertEqual(response.status_code, 200)

    def test_topic_sitemap_content(self):
        topic_1 = TopicFactory()
        topic_2 = TopicFactory()
        topic_3 = TopicFactory()

        response = self.client.get("/sitemap-topics.xml")
        response_content = response.content.decode()
        self.assertIn(
            (
                f"<loc>http://example.com/encyclopedia/{topic_1.pk}/</loc>"
                f"<lastmod>{topic_1.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                f"<loc>http://example.com/encyclopedia/{topic_2.pk}/</loc>"
                f"<lastmod>{topic_2.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                f"<loc>http://example.com/encyclopedia/{topic_3.pk}/</loc>"
                f"<lastmod>{topic_3.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )

    def test_article_sitemap_response(self):
        response = self.client.get("/sitemap-articles.xml")
        self.assertEqual(response.status_code, 200)

    def test_article_sitemap_content(self):
        article_1 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-01 12:00:00"), slug="article1"
        )
        article_2 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-02 12:00:00"), slug="article2"
        )
        article_3 = PublishedArticleFactory(
            date_published=make_datetime("2021-01-03 12:00:00"), slug="article3"
        )

        response = self.client.get("/sitemap-articles.xml")
        response_content = response.content.decode()
        self.assertIn(
            (
                "<loc>http://example.com/indepth/2021/01/01/article1/</loc>"
                f"<lastmod>{article_1.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                "<loc>http://example.com/indepth/2021/01/02/article2/</loc>"
                f"<lastmod>{article_2.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                "<loc>http://example.com/indepth/2021/01/03/article3/</loc>"
                f"<lastmod>{article_3.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )

    def test_post_sitemap_response(self):
        response = self.client.get("/sitemap-posts.xml")
        self.assertEqual(response.status_code, 200)

    def test_post_sitemap_content(self):
        post_1 = PublishedPostFactory(
            date_published=make_datetime("2021-01-01 12:00:00")
        )
        post_2 = PublishedPostFactory(
            date_published=make_datetime("2021-01-02 12:00:00")
        )
        post_3 = PublishedPostFactory(
            date_published=make_datetime("2021-01-03 12:00:00")
        )

        response = self.client.get("/sitemap-posts.xml")
        response_content = response.content.decode()
        self.assertIn(
            (
                f"<loc>http://example.com/news/2021/01/01/{post_1.pk}/</loc>"
                f"<lastmod>{post_1.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                f"<loc>http://example.com/news/2021/01/02/{post_2.pk}/</loc>"
                f"<lastmod>{post_2.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )
        self.assertIn(
            (
                f"<loc>http://example.com/news/2021/01/03/{post_3.pk}/</loc>"
                f"<lastmod>{post_3.date_modified.strftime('%Y-%m-%d')}</lastmod>"
            ),
            response_content,
        )

    def test_archive_sitemap_response(self):
        response = self.client.get("/sitemap-archives.xml")
        self.assertEqual(response.status_code, 200)

    def test_archive_sitemap_content_diary_months(self):
        "It should include links to the diary month archive pages"
        response = self.client.get("/sitemap-archives.xml")
        response_content = response.content.decode()

        self.assertIn("<loc>http://example.com/diary/1660/01/</loc>", response_content)
        self.assertIn("<loc>http://example.com/diary/1661/02/</loc>", response_content)

    def test_archive_sitemap_content_encyclopedia_categories(self):
        "It should include links to the encyclopedia category pages"
        root = Category.add_root(title="Animals", slug="animals")
        Category.objects.get(pk=root.pk).add_child(title="Dogs", slug="dogs")

        response = self.client.get("/sitemap-archives.xml")
        response_content = response.content.decode()

        self.assertIn(
            "<loc>http://example.com/encyclopedia/animals/</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/encyclopedia/animals/dogs/</loc>",
            response_content,
        )

    def test_archive_sitemap_content_news_categories(self):
        "It should include links to the news category pages"
        response = self.client.get("/sitemap-archives.xml")
        response_content = response.content.decode()

        for slug, label in Post.Category.choices:
            self.assertIn(
                f"<loc>http://example.com/news/{slug}/</loc>", response_content
            )

    def test_archive_sitemap_content_summaries(self):
        "It should include links to the diary summary pages"
        response = self.client.get("/sitemap-archives.xml")
        response_content = response.content.decode()

        self.assertIn(
            "<loc>http://example.com/diary/summary/1660/</loc>", response_content
        )
        self.assertIn(
            "<loc>http://example.com/diary/summary/1661/</loc>", response_content
        )
