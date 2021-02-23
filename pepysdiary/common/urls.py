from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemaps_views
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView

from rest_framework.documentation import include_docs_urls

from pepysdiary.common import sitemaps
from pepysdiary.common.views import (
    DiaryMonthRedirectView,
    DiaryEntryRedirectView,
    LetterRedirectView,
    EncyclopediaCategoryRedirectView,
    EncyclopediaTopicRedirectView,
    ArticleRedirectView,
    PostRedirectView,
    SummaryYearRedirectView,
    HomeView,
    GoogleSearchView,
    SearchView,
    RecentView,
)


admin.autodiscover()


urlpatterns = []


# Redirects from old Movable Type URLs to new ones.
urlpatterns += [
    re_path(
        r"^favicon\.ico$",
        RedirectView.as_view(
            url="%scommon/img/favicons/favicon.ico" % settings.STATIC_URL,
            permanent=True,
        ),
    ),
    # Redirect any URL with a trailiing 'index.php' to its base URL.
    # eg /diary/1660/01/01/index.php to /diary/1660/01/01/
    re_path(
        r"^(?P<base_url>.*?)index\.php$",
        RedirectView.as_view(url="%(site_url)s%(base_url)s", permanent=True),
        kwargs={"site_url": reverse_lazy("home")},
    ),
    # For testing the 500 template:
    re_path(r"^errors/500/$", TemplateView.as_view(template_name="500.html")),
    # DIARY.
    # From main /archive/ page.
    re_path(
        r"^archive/$",
        RedirectView.as_view(url=reverse_lazy("entry_archive"), permanent=True),
    ),
    # From /archive/1660/01/ URLs:
    re_path(
        r"^archive/(?P<year>\d{4})/(?P<month>\d{2})/$",
        DiaryMonthRedirectView.as_view(permanent=True),
    ),
    # From /archive/1660/01/01/index.php URLs:
    re_path(
        r"^archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(index\.php)?$",
        DiaryEntryRedirectView.as_view(permanent=True),
    ),
    # The URL of the RSS feed that Feedburner fetches.
    re_path(
        r"^syndication/full-fb\.rdf$",
        RedirectView.as_view(url=reverse_lazy("entry_rss"), permanent=True),
    ),
    # Used on LiveJournal.
    re_path(
        r"^syndication/rdf\.php$",
        RedirectView.as_view(
            url="http://feeds.feedburner.com/PepysDiary", permanent=True
        ),
    ),
    re_path(
        r"^syndication/full\.rdf$",
        RedirectView.as_view(
            url="http://feeds.feedburner.com/PepysDiary", permanent=True
        ),
    ),
    # LETTERS.
    # From /letters/1660/01/01/slug-field.php URLs:
    re_path(
        r"^letters/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)\.php$",  # noqa: E501
        LetterRedirectView.as_view(permanent=True),
    ),
    # ENCYCLOPEDIA.
    re_path(
        r"^background/$",
        RedirectView.as_view(url=reverse_lazy("encyclopedia"), permanent=True),
    ),
    re_path(
        r"^background/familytree/$",
        RedirectView.as_view(
            url=reverse_lazy("encyclopedia_familytree"), permanent=True
        ),
    ),
    re_path(
        r"^background/maps/$",
        RedirectView.as_view(url=reverse_lazy("category_map"), permanent=True),
    ),
    re_path(
        r"^background/(?P<slugs>[\w_\/]+)\.php$",
        EncyclopediaCategoryRedirectView.as_view(permanent=True),
    ),
    re_path(r"^p/(?P<pk>\d+)\.php$", EncyclopediaTopicRedirectView.as_view(permanent=True)),
    # The URL of the RSS feed that Feedburner fetches.
    re_path(
        r"^syndication/encyclopedia-fb\.rdf$",
        RedirectView.as_view(url=reverse_lazy("topic_rss"), permanent=True),
    ),
    # IN-DEPTH.
    # From /indepth/archive/2012/05/31/slug_field.php URLs:
    re_path(
        r"^indepth/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w_]+)\.php$",  # noqa: E501
        ArticleRedirectView.as_view(permanent=True),
    ),
    # The URL of the RSS feed that Feedburner fetches.
    re_path(
        r"^syndication/indepth-fb\.rdf$",
        RedirectView.as_view(url=reverse_lazy("article_rss"), permanent=True),
    ),
    # SITE NEWS.
    # From main Site News front page.
    re_path(
        r"^about/news/$", RedirectView.as_view(url=reverse_lazy("news"), permanent=True)
    ),
    # From /about/archive/2012/05/31/3456.php URLs:
    re_path(
        r"^about/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<pk>\d+)\.php$",  # noqa: E501
        PostRedirectView.as_view(permanent=True),
    ),
    # The URL of the RSS feed that Feedburner fetches.
    re_path(
        r"^syndication/recentnews-fb\.rdf$",
        RedirectView.as_view(url=reverse_lazy("post_rss"), permanent=True),
    ),
    # SUMMARYIES.
    re_path(
        r"^about/history/(?:index.php)?$",
        RedirectView.as_view(url=reverse_lazy("diary_summary"), permanent=True),
    ),
    re_path(
        r"^about/history/(?P<year>\d{4})/$",
        SummaryYearRedirectView.as_view(permanent=True),
    ),
    re_path(
        r"^about/support/$",
        RedirectView.as_view(url=reverse_lazy("about"), permanent=True),
    ),
]

# Flatpages URLs.
urlpatterns += [
    re_path(r"^about/$", flatpages_views.flatpage, {"url": "/about/"}, name="about"),
    re_path(
        r"^about/annotations/$",
        flatpages_views.flatpage,
        {"url": "/about/annotations/"},
        name="about_annotations",
    ),
    re_path(
        r"^about/faq/$",
        flatpages_views.flatpage,
        {"url": "/about/faq/"},
        name="about_faq",
    ),
    re_path(
        r"^about/formats/$",
        flatpages_views.flatpage,
        {"url": "/about/formats/"},
        name="about_formats",
    ),
    re_path(
        r"^about/text/$",
        flatpages_views.flatpage,
        {"url": "/about/text/"},
        name="about_text",
    ),
    re_path(
        r"^diary/1893-introduction/$",
        flatpages_views.flatpage,
        {"url": "/diary/1893-introduction/"},
        name="1893_introduction",
    ),
    re_path(
        r"^diary/1893-introduction/pepys/$",
        flatpages_views.flatpage,
        {"url": "/diary/1893-introduction/pepys/"},
        name="1893_introduction_pepys",
    ),
    re_path(
        r"^diary/1893-introduction/preface/$",
        flatpages_views.flatpage,
        {"url": "/diary/1893-introduction/preface/"},
        name="1893_introduction_preface",
    ),
    re_path(
        r"^diary/1893-introduction/previous/$",
        flatpages_views.flatpage,
        {"url": "/diary/1893-introduction/previous/"},
        name="1893_introduction_previous",
    ),
    re_path(
        r"^diary/summary/$",
        flatpages_views.flatpage,
        {"url": "/diary/summary/"},
        name="diary_summary",
    ),
    re_path(
        r"^encyclopedia/familytree/$",
        flatpages_views.flatpage,
        {"url": "/encyclopedia/familytree/"},
        name="encyclopedia_familytree",
    ),
]


sitemaps = {
    "main": sitemaps.StaticSitemap,
    "entries": sitemaps.EntrySitemap,
    "letters": sitemaps.LetterSitemap,
    "topics": sitemaps.TopicSitemap,
    "articles": sitemaps.ArticleSitemap,
    "posts": sitemaps.PostSitemap,
    "archives": sitemaps.ArchiveSitemap,
    "flatpages": FlatPageSitemap,
}


# The main URL conf for actual pages, not redirects.
urlpatterns += [
    re_path(r"^$", HomeView.as_view(), name="home"),
    re_path(
        r"^sitemap\.xml$",
        cache_page(86400)(sitemaps_views.index),
        {"sitemaps": sitemaps, "sitemap_url_name": "sitemaps"},
        name="sitemap",
    ),
    re_path(
        r"^sitemap-(?P<section>.+)\.xml$",
        cache_page(86400)(sitemaps_views.sitemap),
        {"sitemaps": sitemaps},
        name="sitemaps",
    ),
    re_path(
        r"^robots\.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    re_path(r"^google-search/$", GoogleSearchView.as_view(), name="google-search"),
    re_path(r"^search/$", SearchView.as_view(), name="search"),
    re_path(r"^recent/$", RecentView.as_view(), name="recent"),
    re_path(r"^diary/", include("pepysdiary.diary.urls")),
    re_path(r"^letters/", include("pepysdiary.letters.urls")),
    re_path(r"^encyclopedia/", include("pepysdiary.encyclopedia.urls")),
    re_path(r"^indepth/", include("pepysdiary.indepth.urls")),
    re_path(r"^news/", include("pepysdiary.news.urls")),
    re_path(r"^annotations/", include("django_comments.urls")),
    re_path(r"^annotations/flagging/", include("pepysdiary.annotations.urls")),
    re_path(r"^account/", include("pepysdiary.membership.urls")),
    re_path(r"^backstage/", admin.site.urls),
]


# API stuff

urlpatterns += [
    re_path(r"^api/docs/", include_docs_urls(title="The Diary of Samuel Pepys API")),
    re_path(r"^api/v1/", include("pepysdiary.api.urls")),
]


admin.site.site_header = "The Diary of Samuel Pepys admin"

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ]
