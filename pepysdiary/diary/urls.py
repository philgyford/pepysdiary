from django.urls import re_path

from pepysdiary.diary.views import (
    EntryDetailView,
    EntryMonthArchiveView,
    EntryArchiveView,
    SummaryYearArchiveView,
    LatestEntriesFeed,
)


# ALL REDIRECTS are in common/urls.py.

urlpatterns = [
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
        EntryDetailView.as_view(),
        name="entry_detail",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/$",
        EntryMonthArchiveView.as_view(),
        name="entry_month_archive",
    ),
    re_path(r"^$", EntryArchiveView.as_view(), name="entry_archive"),
    re_path(
        r"^summary/(?P<year>\d{4})/$",
        SummaryYearArchiveView.as_view(),
        name="summary_year_archive",
    ),
    re_path(r"^rss/$", LatestEntriesFeed(), name="entry_rss"),
]
