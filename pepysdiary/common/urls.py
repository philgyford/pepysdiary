from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemaps_views
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from pepysdiary.common import sitemaps
from pepysdiary.common.views import *


admin.autodiscover()

# Redirects from old Movable Type URLs to new ones.
urlpatterns = [

    url(r'^favicon\.ico$', RedirectView.as_view(
                    url='%simg/favicons/favicon.ico' % settings.STATIC_URL,
                    permanent=True)),

    # Redirect any URL with a trailiing 'index.php' to its base URL.
    # eg /diary/1660/01/01/index.php to /diary/1660/01/01/
    url(r'^(?P<base_url>.*?)index\.php$', RedirectView.as_view(
                            url='%(site_url)s%(base_url)s', permanent=True),
                            kwargs={'site_url': reverse_lazy('home')}),

    # DIARY.

    # From main /archive/ page.
    url(r'^archive/$', RedirectView.as_view(
                            url=reverse_lazy('entry_archive'), permanent=True)),

    # From /archive/1660/01/ URLs:
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/$',
        DiaryMonthRedirectView.as_view(permanent=True)
    ),

    # From /archive/1660/01/01/index.php URLs:
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(index\.php)?$',
        DiaryEntryRedirectView.as_view(permanent=True)
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/full-fb\.rdf$', RedirectView.as_view(
                            url=reverse_lazy('entry_rss'), permanent=True)),
    # Used on LiveJournal.
    url(r'^syndication/rdf\.php$', RedirectView.as_view(
                url='http://feeds.feedburner.com/PepysDiary', permanent=True)),
    url(r'^syndication/full\.rdf$', RedirectView.as_view(
                url='http://feeds.feedburner.com/PepysDiary', permanent=True)),


    # LETTERS.

    # From /letters/1660/01/01/slug-field.php URLs:
    url(r'^letters/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)\.php$',
        LetterRedirectView.as_view(permanent=True)
    ),

    # ENCYCLOPEDIA.

    url(r'^background/$', RedirectView.as_view(
                            url=reverse_lazy('encyclopedia'), permanent=True)),
    url(r'^background/familytree/$', RedirectView.as_view(
                url=reverse_lazy('encyclopedia_familytree'), permanent=True)),
    url(r'^background/maps/$', RedirectView.as_view(
                            url=reverse_lazy('category_map'), permanent=True)),
    url(r'^background/(?P<slugs>[\w_\/]+)\.php$',
                    EncyclopediaCategoryRedirectView.as_view(permanent=True)),

    url(r'^p/(?P<pk>\d+)\.php$',
                        EncyclopediaTopicRedirectView.as_view(permanent=True)),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/encyclopedia-fb\.rdf$', RedirectView.as_view(
                            url=reverse_lazy('topic_rss'), permanent=True)),

    # IN-DEPTH.

    # From /indepth/archive/2012/05/31/slug_field.php URLs:
    url(r'^indepth/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w_]+)\.php$',
        ArticleRedirectView.as_view(permanent=True)
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/indepth-fb\.rdf$', RedirectView.as_view(
                            url=reverse_lazy('article_rss'), permanent=True)),

    # SITE NEWS.

    # From main Site News front page.
    url(r'^about/news/$',RedirectView.as_view(
                                    url=reverse_lazy('news'), permanent=True)),

    # From /about/archive/2012/05/31/3456.php URLs:
    url(r'^about/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<pk>\d+)\.php$',
        PostRedirectView.as_view(permanent=True)
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/recentnews-fb\.rdf$', RedirectView.as_view(
                                url=reverse_lazy('post_rss'), permanent=True)),

    # SUMMARYIES.

    url(r'^about/history/(?:index.php)?$', RedirectView.as_view(
                            url=reverse_lazy('diary_summary'), permanent=True)),

    url(r'^about/history/(?P<year>\d{4})/$',
                            SummaryYearRedirectView.as_view(permanent=True)),

    url(r'^about/support/$', RedirectView.as_view(
                                url=reverse_lazy('about'), permanent=True)),
]

# Flatpages URLs.
urlpatterns += [
    url(r'^about/$', flatpages_views.flatpage,
                                            {'url': '/about/'}, name='about'),
    url(r'^about/annotations/$', flatpages_views.flatpage,
                    {'url': '/about/annotations/'}, name='about_annotations'),
    url(r'^about/faq/$', flatpages_views.flatpage,
                                    {'url': '/about/faq/'}, name='about_faq'),
    url(r'^about/formats/$', flatpages_views.flatpage,
                            {'url': '/about/formats/'}, name='about_formats'),
    url(r'^about/text/$', flatpages_views.flatpage,
                                {'url': '/about/text/'}, name='about_text'),
    url(r'^diary/1893-introduction/$', flatpages_views.flatpage,
            {'url': '/diary/1893-introduction/'}, name='1893_introduction'),
    url(r'^diary/1893-introduction/pepys/$', flatpages_views.flatpage,
                                    {'url': '/diary/1893-introduction/pepys/'},
                                    name='1893_introduction_pepys'),
    url(r'^diary/1893-introduction/preface/$', flatpages_views.flatpage,
                                {'url': '/diary/1893-introduction/preface/'},
                                name='1893_introduction_preface'),
    url(r'^diary/1893-introduction/previous/$', flatpages_views.flatpage,
                                {'url': '/diary/1893-introduction/previous/'},
                                name='1893_introduction_previous'),
    url(r'^diary/summary/$', flatpages_views.flatpage,
                            {'url': '/diary/summary/'}, name='diary_summary'),
    url(r'^encyclopedia/familytree/$', flatpages_views.flatpage,
        {'url': '/encyclopedia/familytree/'}, name='encyclopedia_familytree'),
]


sitemaps = {
    'main': sitemaps.StaticSitemap,
    'entries': sitemaps.EntrySitemap,
    'letters': sitemaps.LetterSitemap,
    'topics': sitemaps.TopicSitemap,
    'articles': sitemaps.ArticleSitemap,
    'posts': sitemaps.PostSitemap,
    'archives': sitemaps.ArchiveSitemap,
    'flatpages': FlatPageSitemap,
}


# The main URL conf for actual pages, not redirects.
urlpatterns += [
    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^sitemap\.xml$',
        cache_page(86400)(sitemaps_views.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps', },
        name='sitemap'),

    url(r'^sitemap-(?P<section>.+)\.xml$',
        cache_page(86400)(sitemaps_views.sitemap),
        {'sitemaps': sitemaps},
        name='sitemaps'),

    url(r'^robots\.txt$', TemplateView.as_view(
                    template_name='robots.txt', content_type='text/plain')),

    url(r'^search/$', SearchView.as_view(), name='search'),

    url(r'^recent/$', RecentView.as_view(), name='recent'),

    url(r'^diary/', include('pepysdiary.diary.urls')),
    url(r'^letters/', include('pepysdiary.letters.urls')),
    url(r'^encyclopedia/', include('pepysdiary.encyclopedia.urls')),
    url(r'^indepth/', include('pepysdiary.indepth.urls')),
    url(r'^news/', include('pepysdiary.news.urls')),
    url(r'^annotations/', include('django_comments.urls')),
    url(r'^account/', include('pepysdiary.membership.urls')),

    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
   ] + urlpatterns
