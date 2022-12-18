import calendar
import datetime
import re

import pytz
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django_comments.moderation import CommentModerator, moderator
from markdown import markdown

from ..common.models import OldDateMixin, PepysModel
from ..encyclopedia.models import Topic
from .managers import EntryManager


class Entry(PepysModel, OldDateMixin):
    title = models.CharField(max_length=100, blank=False, null=False)
    diary_date = models.DateField(blank=False, null=False, unique=True)
    text = models.TextField(
        blank=False, null=False, help_text="HTML only, no Markdown."
    )
    footnotes = models.TextField(
        blank=True, null=False, help_text="HTML only, no Markdown."
    )
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    # Will also have a 'topics' ManyToMany field, from Topic.

    comment_name = "annotation"
    old_date_field = "diary_date"

    objects = EntryManager()

    class Meta:
        ordering = ["diary_date"]
        verbose_name_plural = "Entries"
        indexes = [GinIndex(fields=["search_document"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Entry, self).save(*args, **kwargs)
        self._make_references()

    def get_absolute_url(self):
        return reverse(
            "entry_detail",
            kwargs={"year": self.year, "month": self.month, "day": self.day},
        )

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return ((self.title, "A"), (self.text, "B"), (self.footnotes, "C"))

    @property
    def date_published(self):
        """The modern-day datetime this item would be published."""
        year = int(self.year) + settings.YEARS_OFFSET
        month = int(self.month)
        day = int(self.day)
        # If the 17th century date is Feb 29th, but there is no Feb 29th in
        # the modern February, then this will be published on March 1st.
        if month == 2 and day == 29 and calendar.monthrange(year, month)[1] == 28:
            month = 3
            day = 1
        return datetime.datetime(year, month, day, 23, 0, 0).replace(tzinfo=pytz.utc)

    @property
    def short_title(self):
        """
        If self.title is 'Monday 16 September 1661' then
        self.short_title is 'Mon 16 Sep 1661'.
        """
        replacements = {
            "Monday": "Mon",
            "Tuesday": "Tue",
            "Wednesday": "Wed",
            "Thursday": "Thu",
            "Friday": "Fri",
            "Saturday": "Sat",
            "Sunday": "Sun",
            "January": "Jan",
            "February": "Feb",
            "March": "Mar",
            "April": "Apr",
            "May": "May",
            "June": "Jun",
            "July": "Jul",
            "August": "Aug",
            "September": "Sep",
            "October": "Oct",
            "November": "Nov",
            "December": "Dec",
        }

        short_title = self.title
        for k, v in replacements.items():
            short_title = short_title.replace(k, v)

        return short_title

    @property
    def text_for_rss(self):
        """
        Returns self.text but with the links to footnotes removed
        """
        return re.sub(r'<a href="#fn[^"]*?">(\d+)</a>', "\\1", self.text)

    @property
    def footnotes_for_rss(self):
        """
        Returns self.footnotes but with the return links removed, wrapped
        in <aside> tags.
        """
        if self.footnotes:
            footnotes = re.sub(r'<a href="#fnr[^"]*?">&#8617;</a>', "", self.footnotes)
            return f"<aside>{footnotes}</aside>"
        else:
            return ""

    def _make_references(self):
        """
        Sets all the Encyclopedia Topics the text of this entry (and footnotes)
        refers to. Saves them to the database.
        """
        self.topics.clear()
        # Get a list of all the Topic IDs mentioned in text and footnotes:
        ids = re.findall(
            r"pepysdiary.com\/encyclopedia\/(\d+)\/",
            "%s %s" % (self.text, self.footnotes),
        )
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
    enable_field = "allow_comments"


moderator.register(Entry, EntryModerator)


class Summary(PepysModel, OldDateMixin):
    """
    The monthly summaries of diary events.
    """

    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False, help_text="Can use Markdown.")
    text_html = models.TextField(
        blank=False,
        null=False,
        help_text="The text field, with Markdown etc, turned into HTML.",
    )
    summary_date = models.DateField(
        blank=False, null=False, help_text="Only the month and year are relevant."
    )

    old_date_field = "summary_date"

    class Meta:
        ordering = ["summary_date"]
        verbose_name_plural = "Summaries"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.text_html = markdown(self.text)
        super(Summary, self).save(*args, **kwargs)
