# coding: utf-8
from django.db import models

from pepysdiary.common.models import OldDateMixin, PepysModel


class DayEvent(PepysModel, OldDateMixin):

    GADBURY_CHOICE = 10
    PARLIAMENT_CHOICE = 20
    JOSSELIN_CHOICE = 30
    SOURCE_CHOICES = (
        (GADBURY_CHOICE, u"John Gadbury’s London Diary"),
        (PARLIAMENT_CHOICE, u'In Parliament'),
        (JOSSELIN_CHOICE, u"In Earl’s Colne, Essex"),
    )

    title = models.CharField(max_length=255, blank=False, null=False)
    event_date = models.DateField(blank=False, null=False, db_index=True)
    url = models.URLField(max_length=255, blank=True, null=False)
    source = models.IntegerField(blank=True, null=True, choices=SOURCE_CHOICES)

    class Meta:
        ordering = ['event_date', ]
        verbose_name = 'Day Event'

    def __unicode__(self):
        return self.title
