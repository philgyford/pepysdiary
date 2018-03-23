from rest_framework import serializers

from pepysdiary.diary.models import Entry


class EntrySerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='api:entry_detail',
        lookup_field='diary_date'
    )

    # Rename model fields to more publicly-useful names:
    date = serializers.DateField(source='diary_date')
    annotation_count = serializers.IntegerField(source='comment_count')
    last_annotation_time = serializers.DateTimeField(source='last_comment_time')

    class Meta:
        model = Entry
        fields = ('date', 'title', 'text', 'footnotes',
                    'annotation_count', 'last_annotation_time',
                    'url',
                )
