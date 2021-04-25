import datetime
import pytz

from django.conf import settings
from django.db import models

from ..common.managers import ReferredManagerMixin
from ..common.utilities import is_leap_year


class EntryManager(models.Manager, ReferredManagerMixin):
    def most_recent_entry_date(self):
        """
        Returns the date of the most recent diary entry 'published'.
        This is always "today's" date, 353 (or whatever) years ago
        (depending on settings.YEARS_OFFSET).
        Except "today's" entry is only published at 23:00 UK time. Until then
        we see "yesterday's" entry.
        """
        tz = pytz.timezone("Europe/London")
        time_now = datetime.datetime.now().replace(tzinfo=tz)
        if int(time_now.strftime("%H")) < 23:
            # It's before 11pm, so we still show yesterday's entry.
            time_now = time_now - datetime.timedelta(days=1)

        entry_year = int(time_now.strftime("%Y")) - settings.YEARS_OFFSET
        entry_month = int(time_now.strftime("%m"))
        entry_day = int(time_now.strftime("%d"))

        if time_now.strftime("%m-%d") == "02-29" and is_leap_year(entry_year) is False:
            entry_day = entry_day - 1

        return datetime.date(entry_year, entry_month, entry_day)

    def all_years_months(self, month_format="b"):
        """
        The years and months for which there are diary entries.
        By default, or with `month_format='b'` then months are like
        'Jan', 'Feb', etc.
        With `month_format='m' then months are like '01', '02', '03', etc.
        """

        if month_format not in ["b", "m"]:
            raise ValueError("month_format argument should be 'b' or 'm'")

        years_months = (
            (
                "1660",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1661",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1662",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1663",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1664",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1665",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1666",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1667",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            (
                "1668",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ),
            ),
            ("1669", ("Jan", "Feb", "Mar", "Apr", "May")),
        )
        if month_format == "m":
            years_months_m = []
            for year, months in years_months:
                months_m = []
                for count, month in enumerate(months):
                    months_m.append("%02d" % (count + 1))
                years_months_m.append(tuple([year, tuple(months_m)]))
            return tuple(years_months_m)
        else:
            return years_months

    def all_years(self):
        """
        Returns a list of years that we have Diary Entries for.
        Each year is a string. e.g.

            ['1660', '1661', ... '1669']
        """
        years_months = self.all_years_months()
        years = [year for year, months in years_months]
        return years
