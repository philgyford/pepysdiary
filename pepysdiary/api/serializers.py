from rest_framework import serializers

from ..common.utilities import make_url_absolute
from ..diary.models import Entry
from ..encyclopedia.models import Category, Topic


# View names and lookup fields for various detail pages.
# Keeping them in one place.
topics_kwargs = {
    "view_name": "api:topic-detail",
    "lookup_field": "id",
    "lookup_url_kwarg": "topic_id",
}
categories_kwargs = {
    "view_name": "api:category-detail",
    "lookup_field": "slug",
    "lookup_url_kwarg": "category_slug",
}
entries_kwargs = {
    "view_name": "api:entry-detail",
    "lookup_field": "diary_date",
    "lookup_url_kwarg": "entry_date",
}


class BaseSerializer(serializers.ModelSerializer):
    """
    Parent class that includes a `webURL` field for the object's
    get_absolute_url() method.
    """

    lastModifiedTime = serializers.DateTimeField(source="date_modified", read_only=True)

    webURL = serializers.SerializerMethodField()

    def get_webURL(self, obj):
        return make_url_absolute(obj.get_absolute_url())


class CategorySerializer(BaseSerializer):
    "Brief info about each Category for the ListView"

    apiURL = serializers.HyperlinkedIdentityField(**categories_kwargs)

    children = serializers.HyperlinkedRelatedField(
        source="get_children", read_only=True, many=True, **categories_kwargs
    )

    parents = serializers.HyperlinkedRelatedField(
        source="get_ancestors", read_only=True, many=True, **categories_kwargs
    )

    topicCount = serializers.IntegerField(source="topic_count", read_only=True)

    class Meta:
        model = Category
        fields = (
            "slug",
            "title",
            "topicCount",
            "depth",
            "parents",
            "children",
            "apiURL",
            "webURL",
        )


class CategoryListSerializer(CategorySerializer):
    pass


class CategoryDetailSerializer(CategorySerializer):
    """
    Full info about the Category, for the DetailView.

    Includes a list of all Topics in the Category.
    """

    topics = serializers.HyperlinkedIdentityField(
        read_only=True, many=True, **topics_kwargs
    )

    class Meta:
        model = Category
        fields = (
            "slug",
            "title",
            "topicCount",
            "depth",
            "parents",
            "children",
            "topics",
            "apiURL",
            "webURL",
        )


class EntrySerializer(BaseSerializer):
    "Brief info about an Entry for the ListView."

    apiURL = serializers.HyperlinkedIdentityField(
        view_name="api:entry-detail",
        lookup_field="diary_date",
        lookup_url_kwarg="entry_date",
    )

    date = serializers.DateField(source="diary_date", read_only=True)

    class Meta:
        model = Entry
        fields = (
            "date",
            "title",
            "lastModifiedTime",
            "apiURL",
            "webURL",
        )


class EntryListSerializer(EntrySerializer):
    pass


class EntryDetailSerializer(EntrySerializer):
    """
    Full info about an Entry for the DetailView.

    Includes a list of all Topics referred to by the Entry.
    """

    entryHTML = serializers.CharField(source="text", read_only=True)
    footnotesHTML = serializers.CharField(source="footnotes", read_only=True)
    annotationCount = serializers.IntegerField(source="comment_count", read_only=True)
    lastAnnotationTime = serializers.DateTimeField(
        source="last_comment_time", read_only=True
    )

    topics = serializers.HyperlinkedIdentityField(
        read_only=True, many=True, **topics_kwargs
    )

    class Meta:
        model = Entry
        fields = (
            "date",
            "title",
            "entryHTML",
            "footnotesHTML",
            "annotationCount",
            "lastAnnotationTime",
            "topics",
            "lastModifiedTime",
            "apiURL",
            "webURL",
        )


class TopicSerializer(BaseSerializer):
    "Brief information about a Topic."

    apiURL = serializers.HyperlinkedIdentityField(**topics_kwargs)

    orderTitle = serializers.CharField(source="order_title", read_only=True)

    kind = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = (
            "id",
            "title",
            "orderTitle",
            "kind",
            "lastModifiedTime",
            "apiURL",
            "webURL",
        )

    def get_kind(self, instance):
        if instance.is_person:
            return "person"
        elif instance.is_place:
            return "place"
        else:
            return "default"


class TopicListSerializer(TopicSerializer):
    pass


class TopicDetailSerializer(TopicSerializer):
    """
    All information about a Topic, for Detail view.

    Includes a list of all Entries that refer to this Topic.
    """

    # Rename model fields to more publicly-useful names:
    annotationCount = serializers.IntegerField(source="comment_count", read_only=True)
    lastAnnotationTime = serializers.DateTimeField(
        source="last_comment_time", read_only=True
    )
    thumbnailURL = serializers.ImageField(source="thumbnail", read_only=True)

    categories = serializers.HyperlinkedRelatedField(
        read_only=True, many=True, **categories_kwargs
    )

    entries = serializers.HyperlinkedRelatedField(
        source="diary_references", read_only=True, many=True, **entries_kwargs
    )

    wikipediaURL = serializers.URLField(source="wikipedia_url", read_only=True)

    wheatleyHTML = serializers.CharField(source="wheatley_html", read_only=True)

    tooltipText = serializers.CharField(source="tooltip_text", read_only=True)

    class Meta:
        model = Topic
        fields = (
            "id",
            "title",
            "orderTitle",
            # 'summary',
            "wheatleyHTML",
            "tooltipText",
            "wikipediaURL",
            "thumbnailURL",
            "annotationCount",
            "lastAnnotationTime",
            "kind",
            "latitude",
            "longitude",
            "zoom",
            "shape",
            "categories",
            "entries",
            "lastModifiedTime",
            "apiURL",
            "webURL",
        )
