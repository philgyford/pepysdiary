from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets

from ..common.views import CacheMixin
from ..diary.models import Entry
from ..encyclopedia.models import Category, Topic
from .serializers import (
    CategorySerializer, EntrySerializer, TopicSerializer
)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'categories': reverse('api:category_list', request=request, format=format),
        'entries': reverse('api:entry_list', request=request, format=format),
        'topics': reverse('api:topic_list', request=request, format=format),
    })


class CategoryViewSet(CacheMixin, viewsets.ReadOnlyModelViewSet):
    """
    Encyclopedia categories.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Diary entries.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'diary_date'
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Encyclopedia topics.
    """
    cache_timeout = (60 * 15)
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
