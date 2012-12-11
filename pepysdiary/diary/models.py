from django.core.urlresolvers import reverse
from django.db import models

from pepysdiary.common.models import PepysModel


class Entry(PepysModel):
    title = models.CharField(max_length=100, blank=False, null=False)
    diary_date = models.DateField(blank=False, null=False, unique=True)
    text = models.TextField(blank=False, null=False)
    footnotes = models.TextField(blank=True, null=False)
    comment_count = models.IntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['diary_date', ]
        verbose_name_plural = 'Entries'

    def __unicode__(self):
        return self.title

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
