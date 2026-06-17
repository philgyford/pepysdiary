from django.urls import path, re_path

from .feeds import LatestTopicsFeed
from .views import (
    CategoryDetailView,
    CategoryMapView,
    EncyclopediaView,
    TopicDetailView,
)

# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    path("", EncyclopediaView.as_view(), name="encyclopedia"),
    path("rss/", LatestTopicsFeed(), name="topic_rss"),
    path("<int:pk>/", TopicDetailView.as_view(), name="topic_detail"),
    re_path(
        r"^map/(?:(?P<category_id>[0-9]+)/)?$",
        CategoryMapView.as_view(),
        name="category_map",
    ),
    re_path(
        r"^(?P<slugs>[\w\/-]+)/$", CategoryDetailView.as_view(), name="category_detail"
    ),
]
