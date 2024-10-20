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
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$",
        LetterDetailView.as_view(),
        name="letter_detail",
    ),
    re_path(
        r"^person/from/(?P<pk>[\d]+)/$",
        LetterFromPersonView.as_view(),
        name="letter_from_person",
    ),
    re_path(
        r"^person/to/(?P<pk>[\d]+)/$",
        LetterToPersonView.as_view(),
        name="letter_to_person",
    ),
    re_path(
        r"^person/(?P<pk>[\d]+)/$",
        LetterPersonView.as_view(),
        name="letter_person",
    ),
    path("", LetterArchiveView.as_view(), name="letters"),
]
