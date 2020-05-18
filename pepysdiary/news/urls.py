from django.conf.urls import url

from pepysdiary.news.views import (
    LatestPostsFeed,
    PostDetailView,
    PostCategoryArchiveView,
    PostArchiveView,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    url(r"^rss/$", LatestPostsFeed(), name="post_rss"),
    url(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<pk>\d+)/$",
        PostDetailView.as_view(),
        name="post_detail",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/$",
        PostCategoryArchiveView.as_view(),
        name="post_category_archive",
    ),
    url(r"^$", PostArchiveView.as_view(), name="news"),
]
