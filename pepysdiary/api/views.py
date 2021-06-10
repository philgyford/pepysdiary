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
    Listing the possible endpoints for retrieving lists of data.

    Optional query string arguments:

    * `format`, one of `json` or `api` (default)

    e.g. `/api/v1/?format=json`
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
    Returns a list of all the Encyclopedia Categories. The Categories
    are a hierarchical tree structure, and each one may containg zero
    or more Topics.

    Optional query string arguments:

    * `format`, one of `json` or `api` (default)
    * `page` - e.g. `2`

    e.g. `/api/v1/categories/?format=json&page=2`
    """

    queryset = Category.objects.all().order_by("slug")
    serializer_class = CategoryListSerializer


class CategoryDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Returns the Encyclopedia Category specified by a slug,
    e.g. `london` or `music`.

    Each Category lists the API URLs for the zero or more Topics
    within.

    Optional query string arguments:

    * `format`, one of `json` or `api` (default)

    e.g. `/api/v1/categories/music/?format=json`
    """

    lookup_field = "slug"
    lookup_url_kwarg = "category_slug"
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class EntryListView(APICacheMixin, generics.ListAPIView):
    """
    Returns a list of all the Diary Entries, between
    `1660-01-01` and `1669-05-31`.

    Optional query string arguments:

    * `start` - Only fetch Entries from this date forwards, e.g. `1660-01-01`.
    * `end` - Only fetch Entries from this date backwards, e.g. `1669-05-31`.
      Using both `start` and `end` restricts results to between those dates.
    * `format`, one of `json` or `api` (default)
    * `page` - e.g. `2`

    e.g. `/api/v1/entries/?start=1660-01-01&end=1660-12-31&format=json&page=2`
    """

    queryset = Entry.objects.all()
    serializer_class = EntryListSerializer

    def get_queryset(self):
        """
        Optionally filter by year and month query string arguments.
        Either filter by year alone, or year and month.
        """
        queryset = self.queryset
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")

        if start:
            parts = start.split("-")
            start_date = date_from_string(
                parts[0], "%Y", parts[1], "%m", parts[2], "%d", "-"
            )
            queryset = queryset.filter(diary_date__gte=start_date)

        if end:
            parts = end.split("-")
            end_date = date_from_string(
                parts[0], "%Y", parts[1], "%m", parts[2], "%d", "-"
            )
            queryset = queryset.filter(diary_date__lte=end_date)

        return queryset


class EntryDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Returns the Diary Entry specified by a date, e.g. `1660-12-31`.
    Dates range from `1660-01-01` to `1669-05-31`.

    Each Entry lists the API URLs for all the Encyclopedia Topics
    referred to in its text.

    Optional query string arguments:

    * `format`, one of `json` or `api` (default)

    e.g. `/api/v1/entries/1660-12-31/?format=json`
    """

    lookup_field = "diary_date"
    lookup_url_kwarg = "entry_date"
    queryset = Entry.objects.all()
    serializer_class = EntryDetailSerializer


class TopicListView(APICacheMixin, generics.ListAPIView):
    """
    Returns a list of all the Encyclopedia Topics.

    Optional query string arguments:

    * `format`, one of `json` or `api` (default)
    * `page` - e.g. `2`

    e.g. `/api/v1/topics/?format=json&page=2`
    """

    lookup_field = "id"
    lookup_url_kwarg = "topic_id"
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer


class TopicDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Returns the Encyclopedia Topic specified by a numeric ID,
    e.g. `796` or `1075`.

    Each Topic lists the API URLs for one or more Diary Entries in
    which it is mentioned, and the one or more Encyclpedia Categories
    in which it lives.

    Optional query string arguments:

    * `format`, one of `json` or `api` (default)

    e.g. `/api/v1/topics/796/?format=json`
    """

    lookup_field = "id"
    lookup_url_kwarg = "topic_id"
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer
