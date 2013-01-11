from django.conf.urls import *

from pepysdiary.letters.views import *


# ALL REDIRECTS are in common/urls.py.

urlpatterns = patterns('',
    url(r'^rss/$', LatestLettersFeed(), name='letter_rss'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
                            LetterDetailView.as_view(), name='letter_detail'),

    url(r'^person/(?P<pk>[\d]+)/$', LetterPersonView.as_view(),
                                                        name='letter_person'),

    url(r'^$', LetterArchiveView.as_view(), name='letters'),
)
