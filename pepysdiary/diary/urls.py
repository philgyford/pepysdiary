from django.urls import path, re_path

from .feeds import LatestEntriesFeed
from .views import (
    EntryDetailView,
    EntryMonthArchiveView,
    EntryArchiveIndexView,
    SummaryYearArchiveView,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$",
        EntryDetailView.as_view(),
        name="entry_detail",
    ),
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$",
        EntryMonthArchiveView.as_view(),
        name="entry_month_archive",
    ),
    path("", EntryArchiveIndexView.as_view(), name="entry_archive"),
    re_path(
        r"^summary/(?P<year>[0-9]{4})/$",
        SummaryYearArchiveView.as_view(),
        name="summary_year_archive",
    ),
    path("rss/", LatestEntriesFeed(), name="entry_rss"),
]
