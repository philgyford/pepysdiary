from django.urls import path, re_path

from .feeds import LatestPostsFeed
from .views import PostArchiveView, PostCategoryArchiveView, PostDetailView

# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    path("rss/", LatestPostsFeed(), name="post_rss"),
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<pk>[0-9]+)/$",
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
