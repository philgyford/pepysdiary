from django.conf.urls import *

from pepysdiary.diary.views import *


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
                                EntryDetailView.as_view(), name='entry_detail'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
                EntryMonthArchiveView.as_view(), name='entry_month_archive'),

    url(r'^$', EntryArchiveView.as_view(), name='entry_archive'),

    url(r'^summary/(?P<year>\d{4})/$',
                SummaryYearArchiveView.as_view(), name='summary_year_archive'),

    url(r'^rss/$', LatestEntriesFeed(), name='entry_rss'),
]
