from rest_framework import serializers

from ..common.utilities import make_url_absolute
from ..diary.models import Entry
from ..encyclopedia.models import Category, Topic


class BaseSerializer(serializers.ModelSerializer):
    """
    Parent class that includes a `web_url` field for the object's
    get_absolute_url() method.
    """

    web_url = serializers.SerializerMethodField()

    def get_web_url(self, obj):
        return make_url_absolute(obj.get_absolute_url())


class CategorySerializer(BaseSerializer):

    api_url = serializers.HyperlinkedIdentityField(
        view_name='api:category_detail',
        lookup_field='pk'
    )

    class Meta:
        model = Category
        fields = ('id',
                    'slug', 'title', 'topic_count',
                    'api_url', 'web_url',
                )



class EntrySerializer(BaseSerializer):

    api_url = serializers.HyperlinkedIdentityField(
        view_name='api:entry_detail',
        lookup_field='diary_date'
    )

    # Rename model fields to more publicly-useful names:
    date = serializers.DateField(source='diary_date', read_only=True)
    annotation_count = serializers.IntegerField(source='comment_count', read_only=True)
    last_annotation_time = serializers.DateTimeField(source='last_comment_time', read_only=True)

    class Meta:
        model = Entry
        fields = ('date',
                    'title', 'text', 'footnotes',
                    'annotation_count', 'last_annotation_time',
                    'api_url', 'web_url',
                )

class TopicSerializer(BaseSerializer):

    api_url = serializers.HyperlinkedIdentityField(
        view_name='api:topic_detail',
        lookup_field='pk'
    )

    # Rename model fields to more publicly-useful names:
    tooltip = serializers.CharField(source='tooltip_text', read_only=True)
    annotation_count = serializers.IntegerField(source='comment_count', read_only=True)
    last_annotation_time = serializers.DateTimeField(source='last_comment_time', read_only=True)
    thumbnail_url = serializers.ImageField(source='thumbnail', read_only=True)

    class Meta:
        model = Topic
        fields = ('id',
                    'title', 'order_title',
                    'summary', 'wheatley', 'tooltip',
                    'wikipedia_url', 'thumbnail_url',
                    'annotation_count', 'last_annotation_time',
                    'is_person', 'is_place',
                    'latitude', 'longitude', 'zoom', 'shape',
                    'api_url', 'web_url',
                )
