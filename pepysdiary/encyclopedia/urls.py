from django.conf.urls.defaults import *

from pepysdiary.encyclopedia.views import *


# ALL REDIRECTS are in common/urls.py.

urlpatterns = patterns('',
    url(r'^$', EncyclopediaView.as_view(), name='encyclopedia'),

    url(r'^(?P<pk>\d+)/$', TopicDetailView.as_view(),
                                                    name='encyclopedia_topic'),

    url(r'^(?P<slugs>[\w\/]+)/$', CategoryDetailView.as_view(),
                                                name='encyclopedia_category'),
)
