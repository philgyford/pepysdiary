from django.urls import path, re_path

from .feeds import LatestPostsFeed
from .views import (
    PostDetailView,
    PostCategoryArchiveView,
    PostArchiveView,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    path("rss/", LatestPostsFeed(), name="post_rss"),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<pk>\d+)/$",
        PostDetailView.as_view(),
        name="post_detail",
    ),
    re_path(
        r"^(?P<category_slug>[\w-]+)/$",
        PostCategoryArchiveView.as_view(),
        name="post_category_archive",
    ),
    path("", PostArchiveView.as_view(), name="news"),
]
