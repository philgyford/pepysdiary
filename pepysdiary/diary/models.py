import re

from django.core.urlresolvers import reverse
from django.db import models

from pepysdiary.common.models import PepysModel
from pepysdiary.encyclopedia.models import Topic


class Entry(PepysModel):
    title = models.CharField(max_length=100, blank=False, null=False)
    diary_date = models.DateField(blank=False, null=False, unique=True)
    text = models.TextField(blank=False, null=False)
    footnotes = models.TextField(blank=True, null=False)
    comment_count = models.IntegerField(default=0, blank=False, null=False)

    # Will also have a 'topics' ManyToMany field, from Topic.

    class Meta:
        ordering = ['diary_date', ]
        verbose_name_plural = 'Entries'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Entry, self).save(*args, **kwargs)
        self.make_references()

    def get_absolute_url(self):
        return reverse('diary_entry', kwargs={
                'year': self.year,
                'month': self.month,
                'day': self.day,
            })

    @property
    def year(self):
        return self.diary_date.isoformat().split('T')[0].split('-')[0]

    @property
    def month(self):
        return self.diary_date.isoformat().split('T')[0].split('-')[1]

    @property
    def day(self):
        return self.diary_date.isoformat().split('T')[0].split('-')[2]

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
            topic.diary_references.add(self)
