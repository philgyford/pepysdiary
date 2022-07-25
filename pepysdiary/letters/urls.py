from django.urls import path, re_path

from .feeds import LatestLettersFeed
from .views import LetterArchiveView, LetterDetailView, LetterPersonView

# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    path("rss/", LatestLettersFeed(), name="letter_rss"),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$",
        LetterDetailView.as_view(),
        name="letter_detail",
    ),
    re_path(
        r"^person/(?P<pk>[\d]+)/$", LetterPersonView.as_view(), name="letter_person"
    ),
    path("", LetterArchiveView.as_view(), name="letters"),
]
