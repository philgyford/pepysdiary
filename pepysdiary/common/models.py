from django.contrib.sites.models import Site
from django.db import models

from pepysdiary.common.utilities import *


class PepysModel(models.Model):
    """
    All other Models should inherit this.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # Does this item have 'comment's or 'annotation's?
    comment_name = 'comment'

    class Meta:
        abstract = True

    @property
    def short_title(self):
        """
        Child models (eg, Diary Entries) might override this with a more
        bespoke way of generating a short version of its title. 
        """
        if hasattr(self, 'title'):
            return self.title
        else:
            return ''

    def get_a_comment_name(self):
        """
        If we want to print something like "an annotation" or "a comment",
        then call this.
        """
        if self.comment_name[:1] in ['a', 'e', 'h', 'i', 'o', 'u', ]:
            return 'an %s' % self.comment_name
        else:
            return 'a %s' % self.comment_name


class ConfigManager(models.Manager):
    def get_site_config(self):
        """
        Get the config object for the current Site.
        Usage:
            config = Config.objects.get_site_config()
        """
        try:
            config = Config.objects.get(site=Site.objects.get_current())
        except Config.DoesNotExist:
            return None
        return config


class Config(PepysModel):
    """
    Site-wide configuration settings.
    """
    site = models.OneToOneField(Site, on_delete=models.SET_NULL, blank=False,
                                                                    null=True)
    allow_registration = models.BooleanField(default=True, blank=False,
                                                                    null=False)
    allow_login = models.BooleanField(default=True, blank=False, null=False)
    allow_comments = models.BooleanField(default=True, blank=False, null=False)

    use_registration_captcha = models.BooleanField(
        default=False, blank=False, null=False,
        help_text="If checked, people must complete a Captcha field when registering.")
    use_registration_question = models.BooleanField(
        default=False, blank=False, null=False,
        help_text="If checked, people must successfully answer the question below when registering.")
    registration_question = models.CharField(
        max_length=255, blank=True, null=False, default='')
    registration_answer = models.CharField(
        max_length=255, blank=True, null=False, default='',
        help_text="Not case-sensitive.")

    objects = ConfigManager()


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
