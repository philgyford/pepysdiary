import json
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.core.management.base import BaseCommand

from pepysdiary.events.models import DayEvent

FIXTURE_FILE_PATH = (
    settings.BASE_DIR / "pepysdiary" / "events" / "fixtures" / "suntimes-1660-1669.json"
)

FIRST_DATE = (
    datetime.strptime("1660-01-01", "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
)
LAST_DATE = (
    datetime.strptime("1669-05-31", "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
)


class Command(BaseCommand):
    created = 0
    updated = 0
    ignored = 0

    def handle(self, *args, **kwargs):
        with open(FIXTURE_FILE_PATH) as f:
            data = json.load(f)

        for k, v in data.items():
            gregorian = (
                datetime.strptime(k, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
            )
            julian = gregorian - timedelta(days=10)

            if julian >= FIRST_DATE and julian <= LAST_DATE:
                # It's a date in the diary

                # Create times like "8.15 pm":
                sunrise = (
                    datetime.strptime(v["sunrise"], "%Y-%m-%dT%H:%M:%S%z")
                    .strftime("%-I:%M %p")
                    .lower()
                )
                sunset = (
                    datetime.strptime(v["sunset"], "%Y-%m-%dT%H:%M:%S%z")
                    .strftime("%-I:%M %p")
                    .lower()
                )

                self._create_or_update(julian, f"{sunrise} sunrise", 1)
                self._create_or_update(julian, f"{sunset} sunset", 2)

        self.stdout.write(
            "DONE: "
            f"{self.created} created, {self.updated} updated, {self.ignored} the same"
        )

    def _create_or_update(self, date, title, order):
        """
        Creates a DayEvent with this date, title and order, or updates
        the title if one already exists for that date and order.

        date - Date object
        title - String
        order - Integer
        """
        try:
            sunrise = DayEvent.objects.get(
                source=DayEvent.Source.TIMEANDDATE, event_date=date, order=order
            )
        except DayEvent.DoesNotExist:
            DayEvent.objects.create(
                source=DayEvent.Source.TIMEANDDATE,
                event_date=date,
                order=order,
                title=title,
            )
            self.created += 1
        else:
            if title == title:
                self.ignored += 1
            else:
                sunrise.title = title
                sunrise.save(update_fields=["title"])
                self.updated += 1
