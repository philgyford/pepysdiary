import calendar
import datetime
import pytz
import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from django_comments.moderation import CommentModerator, moderator
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

    def all_years_months(self, month_format='b'):
        """
        The years and months for which there are diary entries.
        By default, or with `month_format='b'` then months are like
        'Jan', 'Feb', etc.
        With `month_format='m' then months are like '01', '02', '03', etc.
        """
        years_months = (
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
        if month_format == 'm':
            years_months_m = []
            for year, months in years_months:
                months_m = []
                for count, month in enumerate(months):
                    months_m.append('%02d' % (count + 1))
                years_months_m.append(tuple([year, tuple(months_m)]))
            return tuple(years_months_m)
        else:
            return years_months


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
        year = int(self.year) + settings.YEARS_OFFSET
        month = int(self.month)
        day = int(self.day)
        # If the 17th century date is Feb 29th, but there is no Feb 29th in
        # the modern February, then this will be published on March 1st.
        if month == 2 and day == 29 and calendar.monthrange(year, month)[1] == 28:
            month = 3
            day = 1
        return datetime.datetime(year, month, day, 23, 0, 0).replace(tzinfo=tz)

    @property
    def short_title(self):
        """
        If self.title is 'Monday 16 Septmber 1661' then self.short_title
        is 'Mon 16 Sep 1661'.
        """
        replacements = {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
                'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat',
                'Sunday': 'Sun',
                'January': 'Jan', 'February': 'Feb', 'March': 'Mar',
                'April': 'Apr', 'May': 'May', 'June': 'Jun', 'July': 'Jul',
                'August': 'Aug', 'September': 'Sep', 'October': 'Oct',
                'November': 'Nov', 'December': 'Dec'}

        short_title = self.title 
        for k, v in replacements.iteritems():
            short_title = short_title.replace(k, v)

        return short_title

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
