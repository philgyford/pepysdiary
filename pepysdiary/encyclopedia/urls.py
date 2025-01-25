from django.urls import re_path

from .feeds import LatestTopicsFeed
from .views import (
    CategoryDetailView,
    CategoryMapView,
    EncyclopediaView,
    TopicDetailView,
)

# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(r"^$", EncyclopediaView.as_view(), name="encyclopedia"),
    re_path(r"^rss/$", LatestTopicsFeed(), name="topic_rss"),
    re_path(r"^(?P<pk>[0-9]+)/$", TopicDetailView.as_view(), name="topic_detail"),
    re_path(
        r"^map/(?:(?P<category_id>[0-9]+)/)?$",
        CategoryMapView.as_view(),
        name="category_map",
    ),
    re_path(
        r"^(?P<slugs>[\w\/-]+)/$", CategoryDetailView.as_view(), name="category_detail"
    ),
]
