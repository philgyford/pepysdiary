from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import exception_handler

from ..common.views import CacheMixin
from ..diary.models import Entry
from ..encyclopedia.models import Category, Topic
from .serializers import (
    CategoryDetailSerializer, CategoryListSerializer,
    EntryDetailSerializer, EntryListSerializer,
    TopicDetailSerializer, TopicListSerializer
)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class APICacheMixin(CacheMixin):
    cache_timeout = (60 * 15)


@api_view(['GET'])
def api_root(request, format=None):
    """
    Defines what appears when we go to the top-level URL of the API:
    """
    return Response({
        'categories': reverse('api:category_list', request=request, format=format),
        'entries': reverse('api:entry_list', request=request, format=format),
        'topics': reverse('api:topic_list', request=request, format=format),
    })


class CategoryListView(APICacheMixin, generics.ListAPIView):
    """
    Return a list of all the Encyclopedia Categories.
    """
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Return the Encyclopedia Category specified by `category_slug`.

    Includes a list of all Topics in this Category.

    e.g. `london` or `instruments`.
    """
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class EntryListView(APICacheMixin, generics.ListAPIView):
    """
    Return a list of all the Diary Entries.
    """
    lookup_field = 'diary_date'
    lookup_url_kwarg = 'entry_date'
    queryset = Entry.objects.all()
    serializer_class = EntryListSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned Entries to a year or year+month.
        """
        queryset = self.queryset
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)

        if year is not None:

            # 1. Validate year is numeric.
            try:
                year = int(year)
            except ValueError:
                raise ParseError(
                    detail="Year must be an integer between {} and {} inclusive.".format(
                        year_range[0], year_range[1]))

            # 2. Validate year is within range.

            year_range = self.get_year_range()

            if year < year_range[0] or year > year_range[1]:
                raise ParseError(
                    detail="Year must be between {} and {} inclusive.".format(
                                        year_range[0], year_range[1]))

            if month is None:
                # No month, so just filter by this valid year.
                queryset = queryset.filter(diary_date__year=year)

            else:
                # We have a valid year and a month.

                month_range = self.get_month_range(year)

                error_msg = "For year {}, month must be an integer between {} and {} inclusive.".format(year, month_range[0], month_range[1])

                # 3. Validate month is numeric.
                try:
                    month = int(month)
                except ValueError:
                    raise ParseError(detail=error_msg)

                # 4. Validate month is in range for this year.
                if month < month_range[0] or month > month_range[1]:
                    raise ParseError(detail=error_msg)

                # All good - filter by year and month.
                queryset = queryset.filter(diary_date__year=year,
                                            diary_date__month=month)

        return queryset

    def get_year_range(self):
        "e.g. [1660, 1669],"
        years = Entry.objects.all_years()
        return [int(years[0]), int(years[-1])]

    def get_month_range(self, year):
        years_months = Entry.objects.all_years_months('-m')
        for y, months  in years_months:
            if y == str(year):
                return [int(months[0]), int(months[-1])]
                break


class EntryDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Return the Diary Entry specified by the date (`YYYY-MM-DD`).

    Includes a list of all Topics referred to by this Entry.

    e.g. `1666-09-02`.
    """
    lookup_field = 'diary_date'
    lookup_url_kwarg = 'entry_date'
    queryset = Entry.objects.all()
    serializer_class = EntryDetailSerializer


class TopicListView(APICacheMixin, generics.ListAPIView):
    """
    Return a list of all the Encyclopedia Topics.
    """
    lookup_field = 'id'
    lookup_url_kwarg = 'topic_id'
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer


class TopicDetailView(APICacheMixin, generics.RetrieveAPIView):
    """
    Return the Encyclopedia Topic specified by `topic_id`.

    Includes a list of all Entries that refer to this Topic.

    e.g. `796` or `1075`.
    """
    lookup_field = 'id'
    lookup_url_kwarg = 'topic_id'
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer
