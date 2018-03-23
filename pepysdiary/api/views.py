from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets

from ..diary.models import Entry
from .serializers import EntrySerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'entries': reverse('api:entry_list', request=request, format=format)
    })


class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Diary entries.
    """
    lookup_field = 'diary_date'
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
