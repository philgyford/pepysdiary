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
