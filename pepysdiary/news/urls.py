from django.urls import re_path

from pepysdiary.news.views import (
    LatestPostsFeed,
    PostDetailView,
    PostCategoryArchiveView,
    PostArchiveView,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(r"^rss/$", LatestPostsFeed(), name="post_rss"),
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
    re_path(r"^$", PostArchiveView.as_view(), name="news"),
]
