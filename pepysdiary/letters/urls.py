from django.urls import re_path

from pepysdiary.letters.views import (
    LatestLettersFeed,
    LetterDetailView,
    LetterPersonView,
    LetterArchiveView,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(r"^rss/$", LatestLettersFeed(), name="letter_rss"),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$",
        LetterDetailView.as_view(),
        name="letter_detail",
    ),
    re_path(
        r"^person/(?P<pk>[\d]+)/$", LetterPersonView.as_view(), name="letter_person"
    ),
    re_path(r"^$", LetterArchiveView.as_view(), name="letters"),
]
