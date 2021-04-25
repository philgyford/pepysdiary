from django.contrib.sites.models import Site
from django.db import models


class ReferredManagerMixin(object):
    """
    Used for the managers of Diary Entries and Letters, which both have
    references to Encyclopedia Topics.
    """

    def get_brief_references(self, objects):
        """
        Passed an array (or queryset) of Entry or Letter objects (well,
        any object with a topics ManyToMany relationship to Topic),
        it returns a dict of data about all the Topics those Entries/Letters
        refer to. If a Topic is referred to multiple times across the set of
        Entries/Letters, its data is only included once.
        The returned data will be like:
            {
                '106': {
                    'title': 'George Downing',
                    'text': "1623-1684. An Anglo-Irish solider...",
                    'thumbnail_url': '/media/encyclopedia/thumbnails/106.jpg',
                },
                ...
            }
        Any Topics that don't have tooltip_text or thumbnails will have empty
        strings for those fields.
        """
        topic_data = {}

        for obj in objects:
            for topic in obj.topics.only("pk", "title", "tooltip_text", "thumbnail"):
                if str(topic.pk) not in topic_data:
                    thumbnail_url = ""
                    if topic.thumbnail:
                        thumbnail_url = topic.thumbnail.url
                    topic_data[str(topic.pk)] = {
                        "title": topic.title,
                        "text": topic.tooltip_text,
                        "thumbnail_url": thumbnail_url,
                    }
        return topic_data


class ConfigManager(models.Manager):
    def get_site_config(self):
        """
        Get the config object for the current Site.
        Usage:
            config = Config.objects.get_site_config()
        """
        from .models import Config

        try:
            config = Config.objects.get(site=Site.objects.get_current())
        except Config.DoesNotExist:
            return None
        return config
