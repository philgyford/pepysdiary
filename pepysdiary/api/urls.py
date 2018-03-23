from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views


app_name = 'api'

entry_list = views.EntryViewSet.as_view({
    'get': 'list',
})
entry_detail = views.EntryViewSet.as_view({
    'get': 'retrieve',
})
topic_list = views.TopicViewSet.as_view({
    'get': 'list',
})
topic_detail = views.TopicViewSet.as_view({
    'get': 'retrieve',
})

urlpatterns = [

    url(r'^$', views.api_root),

    url(r'^entries$', entry_list, name='entry_list'),

    url(r'^entries/(?P<diary_date>\d{4}-\d{2}-\d{2})$',
                                entry_detail, name='entry_detail'),

    url(r'^topics$', topic_list, name='topic_list'),

    url(r'^topics/(?P<pk>\d+)$', topic_detail, name='topic_detail'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
