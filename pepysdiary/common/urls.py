from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from pepysdiary.common.views import *


admin.autodiscover()

# Redirects from old Movable Type URLs to new ones.
urlpatterns = patterns('',

    # DIARY.

    # From main /archive/ page.
    url(r'^archive/$', RedirectView.as_view(
                                        url=reverse_lazy('entry_archive'))),

    # From /archive/1660/01/01/index.php URLs:
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(index\.php)?$',
        DiaryEntryRedirectView.as_view()
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/full-fb\.rdf$', RedirectView.as_view(
                                            url=reverse_lazy('entry_rss'))),


    # LETTERS.

    # From /letters/1660/01/01/slug-field.php URLs:
    url(r'^letters/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)\.php$',
        LetterRedirectView.as_view()
    ),

    # ENCYCLOPEDIA.

    url(r'^background/$', RedirectView.as_view(
                                            url=reverse_lazy('encyclopedia'))),
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

    # From /about/archive/2012/05/31/3456/ URLs:
    url(r'^about/archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<pk>\d+)/',
        PostRedirectView.as_view()
    ),

    # The URL of the RSS feed that Feedburner fetches.
    url(r'^syndication/recentnews-fb\.rdf$', RedirectView.as_view(
                                            url=reverse_lazy('post_rss'))),

    # SUMMARY.

    url(r'^about/history/(?P<year>\d{4})/$',
                                            SummaryYearRedirectView.as_view()),
)


# The main URL conf for actual pages, not redirects.
urlpatterns += patterns('',
    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^diary/', include('pepysdiary.diary.urls')),
    url(r'^letters/', include('pepysdiary.letters.urls')),
    url(r'^encyclopedia/', include('pepysdiary.encyclopedia.urls')),
    url(r'^indepth/', include('pepysdiary.indepth.urls')),
    url(r'^news/', include('pepysdiary.news.urls')),

    url(r'^annotations/', include('django.contrib.comments.urls')),

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
