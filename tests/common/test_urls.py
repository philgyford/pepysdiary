from django.test import Client, TestCase
from django.urls import resolve, reverse

from pepysdiary.common import views as common_views
from pepysdiary.encyclopedia.factories import CategoryFactory
from pepysdiary.encyclopedia.views import DEFAULT_MAP_CATEGORY_ID


class RedirectsTestCase(TestCase):
    "Testing all the redirects for legacy URLs"

    def test_favicon(self):
        response = Client().get("/favicon.ico", follow=True)
        self.assertEqual(
            response.redirect_chain, [("/static/common/img/favicons/favicon.ico", 301)]
        )
        self.assertEqual(response.status_code, 200)

    def test_php(self):
        response = Client().get("/diary/1660/01/02/index.php", follow=True)
        self.assertEqual(response.redirect_chain, [("/diary/1660/01/02/", 301)])

    def test_archive(self):
        response = Client().get("/archive/", follow=True)
        self.assertEqual(response.redirect_chain, [("/diary/", 301)])

    def test_archive_month(self):
        response = Client().get("/archive/1660/01/", follow=True)
        self.assertEqual(response.redirect_chain, [("/diary/1660/01/", 301)])

    def test_archive_month_day_php(self):
        response = Client().get("/archive/1660/01/02/index.php", follow=True)
        self.assertEqual(
            response.redirect_chain,
            [("/archive/1660/01/02/", 301), ("/diary/1660/01/02/", 301)],
        )

    def test_diary_feedburner_rss(self):
        response = Client().get("/syndication/full-fb.rdf", follow=True)
        self.assertEqual(response.redirect_chain, [("/diary/rss/", 301)])

    def test_livejournal_rdf_rss(self):
        response = Client().get("/syndication/rdf.php", follow=True)
        self.assertEqual(
            response.redirect_chain, [("https://feeds.feedburner.com/PepysDiary", 301)]
        )

    def test_livejournal_full_rss(self):
        response = Client().get("/syndication/full.rdf", follow=True)
        self.assertEqual(
            response.redirect_chain, [("https://feeds.feedburner.com/PepysDiary", 301)]
        )

    def test_letter_php(self):
        response = Client().get("/letters/1660/01/02/slug-field.php", follow=True)
        self.assertEqual(
            response.redirect_chain, [("/letters/1660/01/02/slug-field/", 301)]
        )

    def test_background(self):
        response = Client().get("/background/", follow=True)
        self.assertEqual(response.redirect_chain, [("/encyclopedia/", 301)])

    def test_familytree(self):
        response = Client().get("/background/familytree/", follow=True)
        self.assertEqual(response.redirect_chain, [("/encyclopedia/familytree/", 301)])

    def test_map(self):
        CategoryFactory(pk=DEFAULT_MAP_CATEGORY_ID)
        response = Client().get("/background/maps/", follow=True)
        self.assertEqual(response.redirect_chain, [("/encyclopedia/map/", 301)])

    def test_category(self):
        response = Client().get("/background/slug_field.php", follow=True)
        self.assertEqual(response.redirect_chain, [("/encyclopedia/slug-field/", 301)])

    def test_topic(self):
        response = Client().get("/p/123.php", follow=True)
        self.assertEqual(response.redirect_chain, [("/encyclopedia/123/", 301)])

    def test_encyclopedia_feedburner_rss(self):
        response = Client().get("/syndication/encyclopedia-fb.rdf", follow=True)
        self.assertEqual(response.redirect_chain, [("/encyclopedia/rss/", 301)])

    def test_indepth_article_php(self):
        response = Client().get(
            "/indepth/archive/2012/05/31/slug_field.php", follow=True
        )
        self.assertEqual(
            response.redirect_chain, [("/indepth/2012/05/31/slug-field/", 301)]
        )

    def test_indepth_feedburner_rss(self):
        response = Client().get("/syndication/indepth-fb.rdf", follow=True)
        self.assertEqual(response.redirect_chain, [("/indepth/rss/", 301)])

    def test_news(self):
        response = Client().get("/about/news/", follow=True)
        self.assertEqual(response.redirect_chain, [("/news/", 301)])

    def test_news_post_php(self):
        response = Client().get("/about/archive/2012/05/31/3456.php", follow=True)
        self.assertEqual(response.redirect_chain, [("/news/2012/05/31/3456/", 301)])

    def test_news_feedburner_rss(self):
        response = Client().get("/syndication/recentnews-fb.rdf", follow=True)
        self.assertEqual(response.redirect_chain, [("/news/rss/", 301)])

    def test_summaries(self):
        response = Client().get("/about/history/", follow=True)
        self.assertEqual(response.redirect_chain, [("/diary/summary/", 301)])

    def test_summaries_indexphp(self):
        response = Client().get("/about/history/index.php", follow=True)
        self.assertEqual(
            response.redirect_chain,
            [("/about/history/", 301), ("/diary/summary/", 301)],
        )

    def test_summaries_year(self):
        response = Client().get("/about/history/1660/", follow=True)
        self.assertEqual(response.redirect_chain, [("/diary/summary/1660/", 301)])

    def test_about_support(self):
        response = Client().get("/about/support/", follow=True)
        self.assertEqual(response.redirect_chain, [("/about/", 301)])


class CommonURLsTestCase(TestCase):
    """
    Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_home_url(self):
        self.assertEqual(reverse("home"), "/")

    def test_home_view(self):
        self.assertEqual(resolve("/").func.__name__, common_views.HomeView.__name__)

    def test_sitemap_url(self):
        self.assertEqual(reverse("sitemap"), "/sitemap.xml")

    def test_sitemap_response(self):
        response = Client().get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)

    def test_sitemaps_section_url(self):
        self.assertEqual(
            reverse("sitemaps", kwargs={"section": "main"}), "/sitemap-main.xml"
        )

    def test_sitemaps_section_response(self):
        response = Client().get(reverse("sitemaps", kwargs={"section": "main"}))
        self.assertEqual(response.status_code, 200)

    def test_robotstxt_url(self):
        self.assertEqual(reverse("robotstxt"), "/robots.txt")

    def test_robotstxt_response(self):
        response = Client().get(reverse("robotstxt"))
        self.assertEqual(response.status_code, 200)

    def test_google_search_url(self):
        self.assertEqual(reverse("google-search"), "/google-search/")

    def test_google_search_view(self):
        self.assertEqual(
            resolve("/google-search/").func.__name__,
            common_views.GoogleSearchView.__name__,
        )

    def test_search_url(self):
        self.assertEqual(reverse("search"), "/search/")

    def test_search_view(self):
        self.assertEqual(
            resolve("/search/").func.__name__,
            common_views.SearchView.__name__,
        )

    def test_recent_url(self):
        self.assertEqual(reverse("recent"), "/recent/")

    def test_recent_view(self):
        self.assertEqual(
            resolve("/recent/").func.__name__,
            common_views.RecentView.__name__,
        )
