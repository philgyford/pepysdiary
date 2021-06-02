from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import exception_handler

from ..common.views import CacheMixin
from ..diary.models import Entry
from ..diary.views import date_from_string
from ..encyclopedia.models import Category, Topic
from .serializers import (
    CategoryDetailSerializer,
    CategoryListSerializer,
    EntryDetailSerializer,
    EntryListSerializer,
    TopicDetailSerializer,
    TopicListSerializer,
)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    return response


class APICacheMixin(CacheMixin):
    cache_timeout = 60 * 15


@api_view(["GET"])
def api_root(request, format=None):
    """
    Defines what appears when we go to the top-level URL of the API:
    """
    return Response(
        {
            "categories": reverse("api:category_list", request=request, format=format),
            "entries": reverse("api:entry_list", request=request, format=format),
            "topics": reverse("api:topic_list", request=request, format=format),
        }
    )


class CategoryListView(APICacheMixin, generics.ListAPIView):
    """
    Return a list of all the Encyclopedia Categories.
    """

    lookup_field = "slug"
    lookup_url_kwarg = "category_slug"
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Return the Encyclopedia Category specified by `category_slug`.

    Includes a list of all Topics in this Category.

    e.g. `london` or `instruments`.
    """

    lookup_field = "slug"
    lookup_url_kwarg = "category_slug"
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class EntryListView(APICacheMixin, generics.ListAPIView):
    """
    Return a list of all the Diary Entries.

    Optional query parameters:

    * `year` - e.g. `1660`.
    * `month` - e.g. `4` or `12`.
    """

    lookup_field = "diary_date"
    lookup_url_kwarg = "entry_date"
    queryset = Entry.objects.all()
    serializer_class = EntryListSerializer

    def get_queryset(self):
        """
        Optionally filter by year and month query string arguments.
        Either filter by year alone, or year and month.
        """
        queryset = self.queryset
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")

        if year is not None:
            year = int(year)
            start_year = year
            end_year = year

            if month is None:
                start_month = 1
                end_month = 12
            else:
                start_month = int(month)
                end_month = int(month) + 1

            if end_month == 13:
                end_year += 1
                end_month = 1

            start_date = date_from_string(
                start_year, "%Y", start_month, "%m", 1, "%d", "-"
            )
            end_date = date_from_string(end_year, "%Y", end_month, "%m", 1, "%d", "-")
            queryset = queryset.filter(
                diary_date__gte=start_date, diary_date__lt=end_date
            )

        return queryset


class EntryDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Return the Diary Entry specified by the date (`YYYY-MM-DD`).

    Includes a list of all Topics referred to by this Entry.

    e.g. `1666-09-02`.
    """

    lookup_field = "diary_date"
    lookup_url_kwarg = "entry_date"
    queryset = Entry.objects.all()
    serializer_class = EntryDetailSerializer


class TopicListView(APICacheMixin, generics.ListAPIView):
    """
    Return a list of all the Encyclopedia Topics.
    """

    lookup_field = "id"
    lookup_url_kwarg = "topic_id"
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer


class TopicDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Return the Encyclopedia Topic specified by `topic_id`.

    Includes a list of all Entries that refer to this Topic.

    e.g. `796` or `1075`.
    """

    lookup_field = "id"
    lookup_url_kwarg = "topic_id"
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer
