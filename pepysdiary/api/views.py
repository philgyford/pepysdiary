from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from rest_framework import viewsets
from rest_framework.views import exception_handler

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


class CachedReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    "Parent class that adds caching to the list() and retrieve() methods."

    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CategoryViewSet(CachedReadOnlyModelViewSet):
    """
    Fetch one or more Encyclopedia Categories. Categories are in a
    tree structure and so has zero or more `parents` and `children`.
    Each Category contains zero or more Topics.

    Return a list of Categories:

    * `categories.api` – browsable view
    * `categories.json` – raw JSON

    Add the `page` to get further pages, e.g.:

    * `categories.api?page=2`
    * `categories.json?page=2`


    Fetch more data about a single Category using its slug, e.g.:

    * `categories/london.api` – browsable view
    * `categories/london.json` – raw JSON
    """

    queryset = Category.objects.all().order_by("slug")
    serializer_class = CategoryListSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "category_slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        else:
            return self.serializer_class


class EntryViewSet(CachedReadOnlyModelViewSet):
    """
    Fetch one or more Diary Entries. Each Entry mentions zero or more
    Encyclopedia Topics.

    Return a list of Entries:

    * `entries.api` – browsable view
    * `entries.json` – raw JSON

    Add the `page` to get further pages, e.g.:

    * `entries.api?page=2`
    * `entries.json?page=2`

    Restrict the list to specific dates, or spans of dates, using the
    `start` and `end` parameters. Entries span from `1660-01-01` to
    `1669-05-31`. e.g.:

    * `entries.api?start=1661-01-01` – Everything after 1st Jan 1661
    * `entries.api?end=1661-12-31` – Everything before 31st Dec 1661
    * `entries.api?start=1661-01-01&end=1661-12-31` – Everything from 1661

    Fetch more data about a single Entry using its date, e.g.:

    * `entries/1660-12-31.api` – browsable view
    * `entries/1660-12-31.json` – raw JSON
    """

    queryset = Entry.objects.all().order_by("diary_date")
    serializer_class = EntryListSerializer
    lookup_field = "diary_date"
    lookup_url_kwarg = "entry_date"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EntryDetailSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        """
        If retrieving a list of Entries, optionally filter by start and
        end query string arguments.
        """
        queryset = self.queryset

        if self.action == "list":
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


class TopicViewSet(CachedReadOnlyModelViewSet):
    """
    Fetch one or more Encyclopedia Topics. Each Topic is contained in
    one or more Categories. Each Topic is mentioned in one or more
    Diary Entries.

    Return a list of Topics:

    * `topics.api` – browsable view
    * `topics.json` – raw JSON

    Add the `page` to get further pages, e.g.:

    * `topics.api?page=2`
    * `topics.json?page=2`

    Fetch more data about a single Topic using its numeric ID, e.g.:

    * `topics/796.api` – browsable view
    * `topics/796.json` – raw JSON
    """
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer
    lookup_field = "id"
    lookup_url_kwarg = "topic_id"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TopicDetailSerializer
        else:
            return self.serializer_class


# class CategoVjryListView(APICacheMixin, generics.ListAPIView):
#     """
#     Returns a list of all the Encyclopedia Categories. The Categories
#     are a hierarchical tree structure, and each one may containg zero
#     or more Topics.

#     Optional query string arguments:

#     * `format`, one of `json` or `api` (default)
#     * `page` - e.g. `2`

#     e.g. `/api/v1/categories/?format=json&page=2`
#     """

#     queryset = Category.objects.all().order_by("slug")
#     serializer_class = CategoryListSerializer


# class CategoryDetailView(APICacheMixin, generics.RetrieveAPIView):
#     """
#     Returns the Encyclopedia Category specified by a slug,
#     e.g. `london` or `music`.

#     Each Category lists the API URLs for the zero or more Topics
#     within.

#     Optional query string arguments:

#     * `format`, one of `json` or `api` (default)

#     e.g. `/api/v1/categories/music/?format=json`
#     """

#     lookup_field = "slug"
#     lookup_url_kwarg = "category_slug"
#     queryset = Category.objects.all()
#     serializer_class = CategoryDetailSerializer


# class EntryListView(APICacheMixin, generics.ListAPIView):
#     """
#     Returns a list of all the Diary Entries, between
#     `1660-01-01` and `1669-05-31`.

#     Optional query string arguments:

#     * `start` - Only fetch Entries from this date forwards, e.g. `1660-01-01`.
#     * `end` - Only fetch Entries from this date backwards, e.g. `1669-05-31`.
#       Using both `start` and `end` restricts results to between those dates.
#     * `format`, one of `json` or `api` (default)
#     * `page` - e.g. `2`

#     e.g. `/api/v1/entries/?start=1660-01-01&end=1660-12-31&format=json&page=2`
#     """

#     queryset = Entry.objects.all()
#     serializer_class = EntryListSerializer

#     def get_queryset(self):
#         """
#         Optionally filter by year and month query string arguments.
#         Either filter by year alone, or year and month.
#         """
#         queryset = self.queryset
#         start = self.request.query_params.get("start")
#         end = self.request.query_params.get("end")

#         if start:
#             parts = start.split("-")
#             start_date = date_from_string(
#                 parts[0], "%Y", parts[1], "%m", parts[2], "%d", "-"
#             )
#             queryset = queryset.filter(diary_date__gte=start_date)

#         if end:
#             parts = end.split("-")
#             end_date = date_from_string(
#                 parts[0], "%Y", parts[1], "%m", parts[2], "%d", "-"
#             )
#             queryset = queryset.filter(diary_date__lte=end_date)

#         return queryset


# class EntryDetailView(APICacheMixin, generics.RetrieveAPIView):
#     """
#     Returns the Diary Entry specified by a date, e.g. `1660-12-31`.
#     Dates range from `1660-01-01` to `1669-05-31`.

#     Each Entry lists the API URLs for all the Encyclopedia Topics
#     referred to in its text.

#     Optional query string arguments:

#     * `format`, one of `json` or `api` (default)

#     e.g. `/api/v1/entries/1660-12-31/?format=json`
#     """

#     lookup_field = "diary_date"
#     lookup_url_kwarg = "entry_date"
#     queryset = Entry.objects.all()
#     serializer_class = EntryDetailSerializer


# class TopicListView(APICacheMixin, generics.ListAPIView):
#     """
#     Returns a list of all the Encyclopedia Topics.

#     Optional query string arguments:

#     * `format`, one of `json` or `api` (default)
#     * `page` - e.g. `2`

#     e.g. `/api/v1/topics/?format=json&page=2`
#     """

#     lookup_field = "id"
#     lookup_url_kwarg = "topic_id"
#     queryset = Topic.objects.all()
#     serializer_class = TopicListSerializer


# class TopicDetailView(APICacheMixin, generics.RetrieveAPIView):
#     """
#     Returns the Encyclopedia Topic specified by a numeric ID,
#     e.g. `796` or `1075`.

#     Each Topic lists the API URLs for one or more Diary Entries in
#     which it is mentioned, and the one or more Encyclpedia Categories
#     in which it lives.

#     Optional query string arguments:

#     * `format`, one of `json` or `api` (default)

#     e.g. `/api/v1/topics/796/?format=json`
#     """

#     lookup_field = "id"
#     lookup_url_kwarg = "topic_id"
#     queryset = Topic.objects.all()
#     serializer_class = TopicDetailSerializer
