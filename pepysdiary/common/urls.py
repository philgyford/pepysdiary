from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemaps_views
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView

from pepysdiary.common import sitemaps
from pepysdiary.common.views import *


admin.autodiscover()

# Redirects from old Movable Type URLs to new ones.
urlpatterns = patterns('',

    url(r'^favicon\.ico$', RedirectView.as_view(
                            url='%simg/favicon.ico' % settings.STATIC_URL)),

    # Redirect any URL with a trailiing 'index.php' to its base URL.
    # eg /diary/1660/01/01/index.php to /diary/1660/01/01/
    url(r'^(?P<base_url>.*?)index\.php$', RedirectView.as_view(
                                url='%(site_url)s%(base_url)s'),
                                kwargs={'site_url': reverse_lazy('home')}),

    # DIARY.

    # From main /archive/ page.
    url(r'^archive/$', RedirectView.as_view(
                                        url=reverse_lazy('entry_archive'))),

    # From /archive/1660/01/ URLs:
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/$',
        DiaryMonthRedirectView.as_view()
    ),

    # From /archive/1660/01/01/index.php URLs:
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(index\.php)?$',
        DiaryEntryRedirectView.as_view()
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/full-fb\.rdf$', RedirectView.as_view(
                                            url=reverse_lazy('entry_rss'))),
    # Used on LiveJournal.
    url(r'^syndication/rdf\.php$', RedirectView.as_view(
                                url='http://feeds.feedburner.com/PepysDiary')),
    url(r'^syndication/full\.rdf$', RedirectView.as_view(
                                url='http://feeds.feedburner.com/PepysDiary')),


    # LETTERS.

    # From /letters/1660/01/01/slug-field.php URLs:
    url(r'^letters/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)\.php$',
        LetterRedirectView.as_view()
    ),

    # ENCYCLOPEDIA.

    url(r'^background/$', RedirectView.as_view(
                                            url=reverse_lazy('encyclopedia'))),
    url(r'^background/familytree/$', RedirectView.as_view(
                                url=reverse_lazy('encyclopedia_familytree'))),
    url(r'^background/maps/$', RedirectView.as_view(
                                            url=reverse_lazy('category_map'))),
    url(r'^background/(?P<slugs>[\w_\/]+)\.php$',
                                    EncyclopediaCategoryRedirectView.as_view()),

    url(r'^p/(?P<pk>\d+)\.php$', EncyclopediaTopicRedirectView.as_view()),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/encyclopedia-fb\.rdf$', RedirectView.as_view(
                                            url=reverse_lazy('topic_rss'))),

    # IN-DEPTH.

    # From /indepth/archive/2012/05/31/slug_field.php URLs:
    url(r'^indepth/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w_]+)\.php$',
        ArticleRedirectView.as_view()
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/indepth-fb\.rdf$', RedirectView.as_view(
                                            url=reverse_lazy('article_rss'))),

    # SITE NEWS.

    # From main Site News front page.
    url(r'^about/news/$', RedirectView.as_view(url=reverse_lazy('news'))),

    # From /about/archive/2012/05/31/3456.php URLs:
    url(r'^about/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<pk>\d+)\.php$',
        PostRedirectView.as_view()
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/recentnews-fb\.rdf$', RedirectView.as_view(
                                            url=reverse_lazy('post_rss'))),

    # SUMMARYIES.

    url(r'^about/history/(?:index.php)?$', RedirectView.as_view(
                                        url=reverse_lazy('diary_summary'))),

    url(r'^about/history/(?P<year>\d{4})/$',
                                            SummaryYearRedirectView.as_view()),

    url(r'^about/support/$', RedirectView.as_view(url=reverse_lazy('about'))),
)

# Flatpages URLs.
urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    url(r'^about/annotations/$', 'flatpage', {'url': '/about/annotations/'},
                                                    name='about_annotations'),
    url(r'^about/faq/$', 'flatpage', {'url': '/about/faq/'}, name='about_faq'),
    url(r'^about/formats/$', 'flatpage', {'url': '/about/formats/'},
                                                        name='about_formats'),
    url(r'^about/text/$', 'flatpage', {'url': '/about/text/'},
                                                            name='about_text'),
    url(r'^diary/1893-introduction/$', 'flatpage',
            {'url': '/diary/1893-introduction/'}, name='1893_introduction'),
    url(r'^diary/1893-introduction/pepys/$', 'flatpage',
                                    {'url': '/diary/1893-introduction/pepys/'},
                                    name='1893_introduction_pepys'),
    url(r'^diary/1893-introduction/preface/$', 'flatpage',
                                {'url': '/diary/1893-introduction/preface/'},
                                name='1893_introduction_preface'),
    url(r'^diary/1893-introduction/previous/$', 'flatpage',
                                {'url': '/diary/1893-introduction/previous/'},
                                name='1893_introduction_previous'),
    url(r'^diary/summary/$', 'flatpage', {'url': '/diary/summary/'},
                                                        name='diary_summary'),
    url(r'^encyclopedia/familytree/$', 'flatpage', {
        'url': '/encyclopedia/familytree/'}, name='encyclopedia_familytree'),
)


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
urlpatterns += patterns('',
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

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
