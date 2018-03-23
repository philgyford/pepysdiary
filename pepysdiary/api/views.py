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
    """
    Defines what appears when we go to the top-level URL of the API:
    """
    return Response({
        'categories': reverse('api:category_list', request=request, format=format),
        'entries': reverse('api:entry_list', request=request, format=format),
        'topics': reverse('api:topic_list', request=request, format=format),
    })


class CategoryViewSet(CacheMixin, viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
    Return the Encyclopedia Category specified by `category_slug`.

    e.g. `london` or `instruments`.

    list:
    Return a list of all the Encyclopedia Categories.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryTopicViewSet(CacheMixin, viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of all the Encyclopedia Topics in one Category.

    e.g. `people` or `taverns`.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_queryset(self):
        """
        Filter results by the category_slug.
        Get the Topics for this Category.
        """
        category_slug = self.kwargs.get(self.lookup_url_kwarg, None)

        if category_slug:
            # Checks the Category exists, and if so, return its Topics.
            # Otherwise, return nothing.
            try:
                category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                return self.queryset.none()
            else:
                # All good, return the Category's Topics:
                return category.topics.all()
        else:
            return self.queryset.none()


class EntryViewSet(CacheMixin, viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
    Return the Diary Entry specified by the date (YYYY-MM-DD).

    e.g. `1666-09-02`.

    list:
    Return a list of all the Diary Entries.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'diary_date'
    lookup_url_kwarg = 'entry_date'
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


class TopicViewSet(CacheMixin, viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
    Return the Encyclopedia Topic specified by the ID.

    e.g. `150` or `1023`.

    list:
    Return a list of all the Encyclopedia Topics.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'id'
    lookup_url_kwarg = 'topic_id'
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class TopicEntryViewSet(CacheMixin, viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of all the Diary Entries that mention this Topic.

    e.g. `150` or `1023`.
    """
    cache_timeout = (60 * 15)
    lookup_field = 'id'
    lookup_url_kwarg = 'topic_id'
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer

    def get_queryset(self):
        """
        Get the Diary Entries referred to by this Topic.
        """
        topic_id = self.kwargs.get(self.lookup_url_kwarg, None)

        if topic_id:
            # Checks the Topic exists, and if so, return its Entries.
            # Otherwise, return nothing.
            try:
                topic = Topic.objects.get(pk=topic_id)
            except Topic.DoesNotExist:
                return self.queryset.none()
            else:
                # All good, return the Topic's Entries:
                return topic.diary_references.all().order_by('diary_date')
        else:
            return self.queryset.none()
