from django.conf.urls.defaults import *

from pepysdiary.diary.views import *


urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
                                EntryDetailView.as_view(), name='diary_entry'),
)
