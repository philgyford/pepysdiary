from rest_framework import serializers
from rest_framework.reverse import reverse

from ..common.utilities import make_url_absolute
from ..diary.models import Entry
from ..encyclopedia.models import Category, Topic


# View names and lookup fields for various detail pages.
# Keeping them in one place.
topics_kwargs = {
    'view_name': 'api:topic_detail',
    'lookup_field': 'id',
    'lookup_url_kwarg': 'topic_id',
}
categories_kwargs = {
    'view_name': 'api:category_detail',
    'lookup_field': 'slug',
    'lookup_url_kwarg': 'category_slug',
}
entries_kwargs = {
    'view_name': 'api:entry_detail',
    'lookup_field': 'diary_date',
    'lookup_url_kwarg': 'entry_date',
}


class TopicsMixin(object):
    """
    For Serializers that need to fetch a list of Topic URLs.

    The Serializer should include:

        topics = serializers.SerializerMethodField()
    """

    def get_topics(self, instance):
        """
        Returns a list of URLs to Topics' API detail views.
        We're not using HyperlinkedRelatedField() because that fetches ALL of
        the Topics' data from the database, which is a lot of unncessary stuff.
        """
        request = self.context.get('request')
        topics = []
        qs = instance.topics.values('pk').order_by('pk')

        for topic in qs:
            topics.append(reverse(
                        topics_kwargs['view_name'],
                        kwargs={topics_kwargs['lookup_url_kwarg']: topic['pk']},
                        request=request))

        return topics


class BaseSerializer(serializers.ModelSerializer):
    """
    Parent class that includes a `webURL` field for the object's
    get_absolute_url() method.
    """

    webURL = serializers.SerializerMethodField()

    def get_webURL(self, obj):
        return make_url_absolute(obj.get_absolute_url())


class CategoryListSerializer(BaseSerializer):
    "Brief info about each Category for the ListView"

    apiURL = serializers.HyperlinkedIdentityField(**categories_kwargs)

    children = serializers.HyperlinkedRelatedField(
                                    source='get_children',
                                    read_only=True,
                                    many=True,
                                    **categories_kwargs)

    parents = serializers.HyperlinkedRelatedField(
                                    source='get_ancestors',
                                    read_only=True,
                                    many=True,
                                    **categories_kwargs)

    topicCount = serializers.IntegerField(source='topic_count', read_only=True)

    class Meta:
        model = Category
        fields = ('slug',
                    'title', 'topicCount',
                    'parents', 'children',
                    'apiURL', 'webURL',
                )


class CategoryDetailSerializer(TopicsMixin, CategoryListSerializer):
    """
    Full info about the Category, for the DetailView.

    Includes a list of all Topics in the Category.
    """

    topics = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('slug',
                    'title', 'topicCount',
                    'parents', 'children',
                    'topics',
                    'apiURL', 'webURL',
                )


class EntryListSerializer(BaseSerializer):
    "Brief info about an Entry for the ListView."

    apiURL = serializers.HyperlinkedIdentityField(**entries_kwargs)

    date = serializers.DateField(source='diary_date', read_only=True)

    class Meta:
        model = Entry
        fields = ('date',
                    'title',
                    'apiURL', 'webURL',
                )


class EntryDetailSerializer(TopicsMixin, EntryListSerializer):
    """
    Full info about an Entry for the DetailView.

    Includes a list of all Topics referred to by the Entry.
    """

    entryHTML = serializers.CharField(source='text', read_only=True)
    footnotesHTML = serializers.CharField(source='footnotes', read_only=True)
    annotationCount = serializers.IntegerField(
                                    source='comment_count', read_only=True)
    lastAnnotationTime = serializers.DateTimeField(
                                    source='last_comment_time', read_only=True)

    topics = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ('date',
                    'title', 'entryHTML', 'footnotesHTML',
                    'annotationCount', 'lastAnnotationTime',
                    'topics',
                    'apiURL', 'webURL',
                )


class TopicListSerializer(BaseSerializer):
    "Brief information about a Topic."

    apiURL = serializers.HyperlinkedIdentityField(**topics_kwargs)

    orderTitle = serializers.CharField(source='order_title', read_only=True)

    isPerson = serializers.BooleanField(source='is_person', read_only=True)

    isPlace = serializers.BooleanField(source='is_place', read_only=True)

    class Meta:
        model = Topic
        fields = ('id',
                    'title', 'orderTitle',
                    'isPerson', 'isPlace',
                    'apiURL', 'webURL',
                )


class TopicDetailSerializer(TopicListSerializer):
    """
    All information about a Topic, for Detail view.

    Includes a list of all Entries that refer to this Topic.
    """

    # Rename model fields to more publicly-useful names:
    annotationCount = serializers.IntegerField(
                                source='comment_count', read_only=True)
    lastAnnotationTime = serializers.DateTimeField(
                                source='last_comment_time', read_only=True)
    thumbnailURL = serializers.ImageField(
                                source='thumbnail', read_only=True)

    categories = serializers.HyperlinkedRelatedField(
                                        read_only=True,
                                        many=True,
                                        **categories_kwargs)

    entries = serializers.SerializerMethodField()

    wikipediaURL = serializers.URLField(source='wikipedia_url', read_only=True)

    wheatleyHTML = serializers.CharField(source='wheatley_html', read_only=True)

    tooltipText = serializers.CharField(source='tooltip_text', read_only=True)

    class Meta:
        model = Topic
        fields = ('id',
                    'title', 'orderTitle',
                    # 'summary',
                    'wheatleyHTML', 'tooltipText',
                    'wikipediaURL', 'thumbnailURL',
                    'annotationCount', 'lastAnnotationTime',
                    'isPerson', 'isPlace',
                    'latitude', 'longitude', 'zoom', 'shape',
                    'categories', 'entries',
                    'apiURL', 'webURL',
                )

    def get_entries(self, instance):
        """
        Returns a list of URLs to Entries' API detail views.
        We're not using HyperlinkedRelatedField() because that fetches ALL of
        the Entries' data from the database, which is a lot of unncessary stuff.
        """
        request = self.context.get('request')
        entries = []
        qs = instance.diary_references.values('diary_date').order_by('diary_date')

        for entry in qs:
            entries.append(reverse(
                entries_kwargs['view_name'],
                kwargs={entries_kwargs['lookup_url_kwarg']: entry['diary_date']},
                request=request))

        return entries
