from django.contrib.sites.models import Site
from django.db import models

from pepysdiary.common.utilities import *


class PepysModel(models.Model):
    """
    All other Models should inherit this.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Config(PepysModel):
    """
    Site-wide configuration settings.
    """
    site = models.OneToOneField(Site, blank=False, null=False)
    allow_registration = models.BooleanField(default=True, blank=False,
                                                                    null=False)
    allow_login = models.BooleanField(default=True, blank=False, null=False)
    allow_comments = models.BooleanField(default=True, blank=False, null=False)


class OldDateMixin(object):
    """
    Because strftime can't cope with very old dates, we have to get
    year/month/day like this...

    Used for Diary Entries, Diary Summaries and Letters.

    Each object using this should define `old_date_field`, which should match
    the DateTimeField or DateField which we use to return dates. eg:
        old_date_field = 'diary_date'
    """
    old_date_field = None

    def get_old_date(self):
        if (not hasattr(self, self.old_date_field)) or \
                                                (self.old_date_field is None):
            raise AttributeError("Objects using OldDateMixin should define"
                                                        "`old_date_field`.")
        return getattr(self, self.old_date_field)

    @property
    def year(self):
        """Year of the Entry like '1660', '1661', etc."""
        return get_year(self.get_old_date())

    @property
    def month(self):
        """Month of the Entry like '01', '02', '12', etc."""
        return get_month(self.get_old_date())

    @property
    def month_b(self):
        """Month of the Entry like 'Jan', 'Feb', 'Dec', etc."""
        return get_month_b(self.get_old_date())

    @property
    def day(self):
        """Day of the Entry like '01', '02', '31', etc."""
        return get_day(self.get_old_date())

    @property
    def day_e(self):
        """Day of the Entry like '1', '2', '31', etc."""
        return get_day_e(self.get_old_date())


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
            for topic in obj.topics.only(
                                'pk', 'title', 'tooltip_text', 'thumbnail'):
                if str(topic.pk) not in topic_data:
                    thumbnail_url = ''
                    if topic.thumbnail:
                        thumbnail_url = topic.thumbnail.url
                    topic_data[str(topic.pk)] = {
                        'title': topic.title,
                        'text': topic.tooltip_text,
                        'thumbnail_url': thumbnail_url,
                    }
        return topic_data
