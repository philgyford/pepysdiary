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
    Fetch one or more Encyclopedia Categories.

    Categories are in a tree structure and so each one has zero or more
    `parents` and `children`.

    Each Category contains zero or more Topics.

    Add the `page` to get further pages of results, e.g.:

    * `categories?page=2`

    Fetch more data about a single Category using its slug, e.g.:

    * `categories/london`
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
    Fetch one or more Diary Entries.

    Each Entry mentions zero or more Encyclopedia Topics.

    Add the `page` to get further pages of results, e.g.:

    * `entries?page=2`

    Restrict the list to specific dates, or spans of dates, using the
    `start` and `end` parameters. Entries span from `1660-01-01` to
    `1669-05-31` inclusive. e.g.:

    * `entries?start=1661-01-01` – Everything on and after 1st Jan 1661
    * `entries?end=1661-12-31` – Everything on and before 31st Dec 1661
    * `entries?start=1661-01-01&end=1661-12-31` – Everything from 1661

    Fetch more data about a single Entry using its date, e.g.:

    * `entries/1660-12-31`
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
    Fetch one or more Encyclopedia Topics.

    Each Topic is contained in one or more Categories.

    Each Topic is mentioned in one or more Diary Entries.

    Add the `page` to get further pages of results, e.g.:

    * `topics?page=2`

    Fetch more data about a single Topic using its numeric ID, e.g.:

    * `topics/796`
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
