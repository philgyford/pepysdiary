from django.urls import path, re_path

from .feeds import LatestLettersFeed
from .views import (
    LetterArchiveView,
    LetterDetailView,
    LetterFromPersonView,
    LetterPersonView,
    LetterToPersonView,
)

# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    path("rss/", LatestLettersFeed(), name="letter_rss"),
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[\w-]+)/$",
        LetterDetailView.as_view(),
        name="letter_detail",
    ),
    re_path(
        r"^person/from/(?P<pk>[0-9]+)/$",
        LetterFromPersonView.as_view(),
        name="letter_from_person",
    ),
    re_path(
        r"^person/to/(?P<pk>[0-9]+)/$",
        LetterToPersonView.as_view(),
        name="letter_to_person",
    ),
    re_path(
        r"^person/(?P<pk>[0-9]+)/$",
        LetterPersonView.as_view(),
        name="letter_person",
    ),
    path(
        "",
        LetterArchiveView.as_view(),
        name="letters",
    ),
]
