from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from pepysdiary.common.views import DiaryEntryRedirectView,\
                                                EncyclopediaTopicRedirectView


admin.autodiscover()

# Redirects from old Movable Type URLs to new ones.
urlpatterns = patterns('',
    # Redirect from old main /archive/ page.
    url(r'^archive/$', RedirectView.as_view(
                                    url=reverse_lazy('diary_entry_archive'))),

    # Redirect from old /archive/1660/01/01/index.php URLs:
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(index\.php)?$',
        DiaryEntryRedirectView.as_view()
    ),

    url(r'^p/(?P<pk>\d+)\.php$', EncyclopediaTopicRedirectView.as_view()),
)

# The main URL conf for actual pages, not redirects.
urlpatterns += patterns('',
    url(r'^diary/', include('pepysdiary.diary.urls')),
    url(r'^encyclopedia/', include('pepysdiary.encyclopedia.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
