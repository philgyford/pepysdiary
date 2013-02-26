import datetime
import pytz
import re

from django.conf import settings
from django.contrib.comments.moderation import CommentModerator, moderator
from django.core.urlresolvers import reverse
from django.db import models

from markdown import markdown

from pepysdiary.common.models import OldDateMixin, PepysModel,\
                                                        ReferredManagerMixin
from pepysdiary.encyclopedia.models import Topic


class EntryManager(models.Manager, ReferredManagerMixin):
    def most_recent_entry_date(self):
        """
        Returns the date of the most recent diary entry 'published'.
        This is always "today's" date, 353 (or whatever) years ago
        (depending on settings.YEARS_OFFSET).
        Except "today's" entry is only published at 23:00 UK time. Until then
        we see "yesterday's" entry.
        """
        tz = pytz.timezone('Europe/London')
        time_now = datetime.datetime.now().replace(tzinfo=tz)
        if int(time_now.strftime('%H')) < 23:
            # It's before 11pm, so we still show yesterday's entry.
            time_now = time_now - datetime.timedelta(days=1)

        return datetime.date(
                        int(time_now.strftime('%Y')) - settings.YEARS_OFFSET,
                        int(time_now.strftime('%m')),
                        int(time_now.strftime('%d'))
                    )

    def all_years_months(self):
        """
        The years and months for which there are diary entries.
        """
        return (
            ('1660', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1661', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1662', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1663', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1664', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1665', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1666', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1667', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1668', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')),
            ('1669', ('Jan', 'Feb', 'Mar', 'Apr', 'May')),
        )


class Entry(PepysModel, OldDateMixin):
    title = models.CharField(max_length=100, blank=False, null=False)
    diary_date = models.DateField(blank=False, null=False, unique=True)
    text = models.TextField(blank=False, null=False,
                                        help_text="HTML only, no Markdown.")
    footnotes = models.TextField(blank=True, null=False,
                                        help_text="HTML only, no Markdown.")
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    # Will also have a 'topics' ManyToMany field, from Topic.

    comment_name = 'annotation'
    old_date_field = 'diary_date'

    objects = EntryManager()

    class Meta:
        ordering = ['diary_date', ]
        verbose_name_plural = 'Entries'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Entry, self).save(*args, **kwargs)
        self.make_references()

    def get_absolute_url(self):
        return reverse('entry_detail', kwargs={
                'year': self.year,
                'month': self.month,
                'day': self.day,
            })

    @property
    def date_published(self):
        """The modern-day datetime this item would be published."""
        tz = pytz.timezone('Europe/London')
        return datetime.datetime(
                            int(self.year) + settings.YEARS_OFFSET,
                            int(self.month),
                            int(self.day),
                            23, 0, 0).replace(tzinfo=tz)

    def make_references(self):
        """
        Sets all the Encyclopedia Topics the text of this entry (and footnotes)
        refers to. Saves them to the database.
        """
        self.topics.clear()
        # Get a list of all the Topic IDs mentioned in text and footnotes:
        ids = re.findall(r'pepysdiary.com\/encyclopedia\/(\d+)\/', '%s %s' % (
                                                    self.text, self.footnotes))
        # Make sure list of Topic IDs is unique:
        # From http://stackoverflow.com/a/480227/250962
        seen = set()
        seen_add = seen.add
        unique_ids = [id for id in ids if id not in seen and not seen_add(id)]

        for id in unique_ids:
            topic = Topic.objects.get(pk=id)
            topic.diary_references.add(self)


class EntryModerator(CommentModerator):
    email_notification = False
    enable_field = 'allow_comments'

moderator.register(Entry, EntryModerator)


class Summary(PepysModel, OldDateMixin):
    """
    The monthly summaries of diary events.
    """
    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False,
                                        help_text="Can use Markdown.")
    text_html = models.TextField(blank=False, null=False,
            help_text="The text field, with Markdown etc, turned into HTML.")
    summary_date = models.DateField(blank=False, null=False,
                            help_text="Only the month and year are relevant.")

    old_date_field = 'summary_date'

    class Meta:
        ordering = ['summary_date', ]
        verbose_name_plural = 'Summaries'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.text_html = markdown(self.text)
        super(Summary, self).save(*args, **kwargs)
