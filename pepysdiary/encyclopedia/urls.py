from django.urls import re_path

from pepysdiary.encyclopedia.views import (
    EncyclopediaView,
    LatestTopicsFeed,
    TopicDetailView,
    CategoryMapView,
    CategoryDetailView,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(r"^$", EncyclopediaView.as_view(), name="encyclopedia"),
    re_path(r"^rss/$", LatestTopicsFeed(), name="topic_rss"),
    re_path(r"^(?P<pk>\d+)/$", TopicDetailView.as_view(), name="topic_detail"),
    re_path(
        r"^map/(?:(?P<category_id>\d+)/)?$",
        CategoryMapView.as_view(),
        name="category_map",
    ),
    re_path(
        r"^(?P<slugs>[\w\/-]+)/$", CategoryDetailView.as_view(), name="category_detail"
    ),
]
