from django.conf.urls import *

from pepysdiary.encyclopedia.views import *


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    url(r'^$', EncyclopediaView.as_view(), name='encyclopedia'),

    url(r'^rss/$', LatestTopicsFeed(), name='topic_rss'),

    url(r'^(?P<pk>\d+)/$', TopicDetailView.as_view(), name='topic_detail'),

    url(r'^map/(?:(?P<category_id>\d+)/)?$', CategoryMapView.as_view(),
                                                        name='category_map'),

    url(r'^(?P<slugs>[\w\/-]+)/$', CategoryDetailView.as_view(),
                                                name='category_detail'),
]
