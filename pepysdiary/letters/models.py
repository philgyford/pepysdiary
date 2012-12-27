# coding: utf-8
import re

from django.core.urlresolvers import reverse
from django.db import models

from pepysdiary.common.models import PepysModel
from pepysdiary.common.utilities import *
from pepysdiary.encyclopedia.models import Topic


class Letter(PepysModel):

    GUY_DE_LA_BEDOYERE_SOURCE = 10
    HELEN_TRUESDELL_HEATH_SOURCE = 20
    SOURCE_CHOICES = (
        (GUY_DE_LA_BEDOYERE_SOURCE, 'Guy de la Bédoyère'),
        (HELEN_TRUESDELL_HEATH_SOURCE, 'Helen Truesdell Heath'),
    )

    title = models.CharField(max_length=100, blank=False, null=False,
        help_text='eg, "Thomas Hill to Samuel Pepys".')
    letter_date = models.DateField(blank=False, null=False)
    display_date = models.CharField(max_length=50, blank=False, null=False,
        help_text='eg "Thursday 27 April 1665". Because days of the week are calculated wrong for old dates.')
    text = models.TextField(blank=False, null=False)
    footnotes = models.TextField(blank=True, null=False)
    excerpt = models.TextField(blank=False, null=False,
        help_text="200 or so characters from the start of the letter, after salutations.")
    sender = models.ForeignKey('encyclopedia.Topic', blank=False, null=False,
                                                related_name='leter_senders')
    recipient = models.ForeignKey('encyclopedia.Topic', blank=False,
                                null=False, related_name='letter_recipients')
    source = models.IntegerField(blank=True, null=True, choices=SOURCE_CHOICES)
    slug = models.SlugField(max_length=50, blank=False, null=False,
                                                unique_for_date='letter_date')
    comment_count = models.IntegerField(default=0, blank=False, null=False)

    # Will also have a 'topics' ManyToMany field, from Topic.

    class Meta:
        ordering = ['letter_date', ]

    def __unicode__(self):
        return '%s: %s' % (self.letter_date, self.title)

    def save(self, *args, **kwargs):
        super(Letter, self).save(*args, **kwargs)
        self.make_references()

    def get_absolute_url(self):
        return reverse('letter_detail', kwargs={
                'year': self.year,
                'month': self.month,
                'day': self.day,
                'slug': self.slug,
            })

    # Because strftime can't cope with very old dates, we have to get
    # year/month/day like this...

    @property
    def year(self):
        """Year of the Letter like '1660', '1661', etc."""
        return get_year(self.letter_date)

    @property
    def month(self):
        """Month of the Letter like '01', '02', '12', etc."""
        return get_month(self.letter_date)

    @property
    def day(self):
        """Day of the Letter like '01', '02', '31', etc."""
        return get_day(self.letter_date)

    def make_references(self):
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
            topic.letter_references.add(self)
