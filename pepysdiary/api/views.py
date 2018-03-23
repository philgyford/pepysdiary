from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets

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


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Encyclopedia categories.
    """
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Diary entries.
    """
    lookup_field = 'diary_date'
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Encyclopedia topics.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
