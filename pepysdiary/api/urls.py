from django.urls import re_path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views


app_name = "api"


urlpatterns = [
    re_path(r"^$", views.api_root),
    re_path(r"^categories$", views.CategoryListView.as_view(), name="category_list"),
    re_path(
        r"^categories/(?P<category_slug>[\w-]+)$",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    re_path(r"^entries$", views.EntryListView.as_view(), name="entry_list"),
    re_path(
        r"^entries/(?P<entry_date>\d{4}-\d{2}-\d{2})$",
        views.EntryDetailView.as_view(),
        name="entry_detail",
    ),
    re_path(r"^topics$", views.TopicListView.as_view(), name="topic_list"),
    re_path(
        r"^topics/(?P<topic_id>\d+)$",
        views.TopicDetailView.as_view(),
        name="topic_detail",
    ),
]


urlpatterns = format_suffix_patterns(urlpatterns)
