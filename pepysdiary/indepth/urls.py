from django.urls import path, re_path

from .feeds import LatestArticlesFeed
from .views import ArticleArchiveView, ArticleCategoryArchiveView, ArticleDetailView

# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    path("rss/", LatestArticlesFeed(), name="article_rss"),
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[\w-]+)/$",
        ArticleDetailView.as_view(),
        name="article_detail",
    ),
    re_path(
        r"^(?P<category_slug>[\w-]+)/$",
        ArticleCategoryArchiveView.as_view(),
        name="article_category_archive",
    ),
    path("", ArticleArchiveView.as_view(), name="indepth"),
]
