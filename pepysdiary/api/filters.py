import django_filters
from django_filters import rest_framework as filters

from ..diary.models import Entry


class EntryFilter(filters.FilterSet):
    year = django_filters.NumberFilter(name="diary_date", lookup_expr="year")
    month = django_filters.NumberFilter(name="diary_date", lookup_expr="month")

    class Meta:
        model = Entry
        fields = (
            "year",
            "month",
        )
