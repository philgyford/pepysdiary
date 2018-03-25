from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

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


class BaseSerializer(serializers.ModelSerializer):
    """
    Parent class that includes a `web_url` field for the object's
    get_absolute_url() method.
    """

    web_url = serializers.SerializerMethodField()

    def get_web_url(self, obj):
        return make_url_absolute(obj.get_absolute_url())


class CategoryListSerializer(BaseSerializer):
    "Brief info about each Category for the ListView"

    api_url = serializers.HyperlinkedIdentityField(**categories_kwargs)

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

    class Meta:
        model = Category
        fields = ('slug',
                    'title', 'topic_count',
                    'parents', 'children',
                    'api_url', 'web_url',
                )


class CategoryDetailSerializer(CategoryListSerializer):
    """
    Full info about the Category, for the DetailView.

    Includes a list of all Topics in the Category.
    """

    topics = serializers.HyperlinkedRelatedField(
                                            read_only=True,
                                            many=True,
                                            **topics_kwargs)

    class Meta:
        model = Category
        fields = ('slug',
                    'title', 'topic_count',
                    'parents', 'children',
                    'topics',
                    'api_url', 'web_url',
                )


class EntryListSerializer(BaseSerializer):
    "Brief info about an Entry for the ListView."

    api_url = serializers.HyperlinkedIdentityField(**entries_kwargs)

    date = serializers.DateField(source='diary_date', read_only=True)

    class Meta:
        model = Entry
        fields = ('date',
                    'title',
                    'api_url', 'web_url',
                )


class EntryDetailSerializer(EntryListSerializer):
    """
    Full info about an Entry for the DetailView.

    Includes a list of all Topics referred to by the Entry.
    """

    entry_html = serializers.CharField(source='text', read_only=True)
    footnotes_html = serializers.CharField(source='footnotes', read_only=True)
    annotation_count = serializers.IntegerField(
                                    source='comment_count', read_only=True)
    last_annotation_time = serializers.DateTimeField(
                                    source='last_comment_time', read_only=True)

    topics = serializers.HyperlinkedRelatedField(
                                            read_only=True,
                                            many=True,
                                            **topics_kwargs)

    class Meta:
        model = Entry
        fields = ('date',
                    'title', 'entry_html', 'footnotes_html',
                    'annotation_count', 'last_annotation_time',
                    'topics',
                    'api_url', 'web_url',
                )


class TopicListSerializer(BaseSerializer):
    "Brief information about a Topic."

    api_url = serializers.HyperlinkedIdentityField(**topics_kwargs)

    class Meta:
        model = Topic
        fields = ('id',
                    'title', 'order_title',
                    'is_person', 'is_place',
                    'api_url', 'web_url',
                )


class TopicDetailSerializer(TopicListSerializer):
    """
    All information about a Topic, for Detail view.

    Includes a list of all Entries that refer to this Topic.
    """

    # Rename model fields to more publicly-useful names:
    annotation_count = serializers.IntegerField(
                                source='comment_count', read_only=True)
    last_annotation_time = serializers.DateTimeField(
                                source='last_comment_time', read_only=True)
    thumbnail_url = serializers.ImageField(
                                source='thumbnail', read_only=True)

    categories = serializers.HyperlinkedRelatedField(
                                        read_only=True,
                                        many=True,
                                        **categories_kwargs)

    entries = serializers.HyperlinkedRelatedField(
                                        source='diary_references',
                                        read_only=True,
                                        many=True,
                                        **entries_kwargs)

    class Meta:
        model = Topic
        fields = ('id',
                    'title', 'order_title',
                    # 'summary',
                    'wheatley_html', 'tooltip_text',
                    'wikipedia_url', 'thumbnail_url',
                    'annotation_count', 'last_annotation_time',
                    'is_person', 'is_place',
                    'latitude', 'longitude', 'zoom', 'shape',
                    'categories', 'entries',
                    'api_url', 'web_url',
                )
