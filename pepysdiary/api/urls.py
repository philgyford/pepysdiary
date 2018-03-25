from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views


app_name = 'api'


category_list = views.CategoryListViewSet.as_view({
    'get': 'list',
})
category_detail = views.CategoryDetailViewSet.as_view({
    'get': 'retrieve',
})
entry_list = views.EntryListViewSet.as_view({
    'get': 'list',
})
entry_detail = views.EntryDetailViewSet.as_view({
    'get': 'retrieve',
})
topic_list = views.TopicListViewSet.as_view({
    'get': 'list',
})
topic_detail = views.TopicDetailViewSet.as_view({
    'get': 'retrieve',
})


urlpatterns = [

    url(r'^$', views.api_root),

    url(r'^categories$', category_list, name='category_list'),

    url(r'^categories/(?P<category_slug>[\w-]+)$',
                                category_detail, name='category_detail'),

    url(r'^entries$', entry_list, name='entry_list'),

    url(r'^entries/(?P<entry_date>\d{4}-\d{2}-\d{2})$',
                                entry_detail, name='entry_detail'),

    # All Topics, or optionally add a category slug for only those topics:
    url(r'^topics$', topic_list, name='topic_list'),

    url(r'^topics/(?P<topic_id>\d+)$', topic_detail, name='topic_detail'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
