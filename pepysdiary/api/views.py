from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics

from ..common.views import CacheMixin
from ..diary.models import Entry
from ..encyclopedia.models import Category, Topic
from .serializers import (
    CategoryDetailSerializer, CategoryListSerializer,
    EntryDetailSerializer, EntryListSerializer,
    TopicDetailSerializer, TopicListSerializer
)


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


class CategoryListView(CacheMixin, generics.ListAPIView):
    """
    Return a list of all the Encyclopedia Categories.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailView(CacheMixin, generics.RetrieveAPIView):
    """
    Return the Encyclopedia Category specified by `category_slug`.

    Includes a list of all Topics in this Category.

    e.g. `london` or `instruments`.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class EntryListView(CacheMixin, generics.ListAPIView):
    """
    Return a list of all the Diary Entries.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'diary_date'
    lookup_url_kwarg = 'entry_date'
    queryset = Entry.objects.all()
    serializer_class = EntryListSerializer


class EntryDetailView(CacheMixin, generics.RetrieveAPIView):
    """
    Return the Diary Entry specified by the date (`YYYY-MM-DD`).

    Includes a list of all Topics referred to by this Entry.

    e.g. `1666-09-02`.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'diary_date'
    lookup_url_kwarg = 'entry_date'
    queryset = Entry.objects.all()
    serializer_class = EntryDetailSerializer


class TopicListView(CacheMixin, generics.ListAPIView):
    """
    Return a list of all the Encyclopedia Topics.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'id'
    lookup_url_kwarg = 'topic_id'
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer


class TopicDetailView(CacheMixin, generics.RetrieveAPIView):
    """
    Return the Encyclopedia Topic specified by `topic_id`.

    Includes a list of all Entries that refer to this Topic.

    e.g. `150` or `1023`.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'id'
    lookup_url_kwarg = 'topic_id'
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer
