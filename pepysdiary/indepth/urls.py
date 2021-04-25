from django.urls import re_path

from .feeds import LatestArticlesFeed
from .views import ArticleDetailView, ArticleArchiveView


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(r"^rss/$", LatestArticlesFeed(), name="article_rss"),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$",
        ArticleDetailView.as_view(),
        name="article_detail",
    ),
    re_path(r"^$", ArticleArchiveView.as_view(), name="indepth"),
]
