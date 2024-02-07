from django.core.exceptions import ImproperlyConfigured

from pepysdiary.common.utilities import (
    get_day,
    get_day_e,
    get_month,
    get_month_b,
    get_year,
)


class OldDateMixin:
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
        if self.old_date_field is None:
            msg = "Objects using OldDateMixin should define" "`old_date_field`."
            raise ImproperlyConfigured(msg)
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
