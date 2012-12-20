from django.conf.urls.defaults import *

from pepysdiary.diary.views import *


# ALL REDIRECTS are in common/urls.py.

urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
                                EntryDetailView.as_view(), name='diary_entry'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
            EntryMonthArchiveView.as_view(), name='diary_entry_month_archive'),

    url(r'^$', EntryArchiveView.as_view(), name='diary_entry_archive'),
)
