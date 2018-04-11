from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views


app_name = 'api'


urlpatterns = [


    url(r'^$', views.api_root),

    url(r'^categories$', views.CategoryListView.as_view(), name='category_list'),

    url(r'^categories/(?P<category_slug>[\w-]+)$',
                                views.CategoryDetailView.as_view(), name='category_detail'),

    url(r'^entries$', views.EntryListView.as_view(), name='entry_list'),

    url(r'^entries/(?P<entry_date>\d{4}-\d{2}-\d{2})$',
                                views.EntryDetailView.as_view(), name='entry_detail'),

    url(r'^topics$', views.TopicListView.as_view(), name='topic_list'),

    url(r'^topics/(?P<topic_id>\d+)$', views.TopicDetailView.as_view(), name='topic_detail'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
