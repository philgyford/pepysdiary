# coding: utf-8
import MySQLdb
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from pepysdiary.events.models import DayEvent

# You'll need to: pip install MySQL-python


class Command(BaseCommand):
    """
    Gets all the Events from the MovableType MySQL database and
    creates a new Django object for each one.

    (The old events are not strictly Movable Type objects, but were custom
    data stored in the same databasea.)

    Usage:
    $ ./manage.py import_mt_events

    And afterwards, do this:
    $ ./manage.py sqlsequencereset 'events'
    and run the SQL commands it gives you.
    """

    option_list = BaseCommand.option_list + (
        make_option(
            "--all",
            action="store_true",
            dest="all",
            default=True,
            help="Import all Events from legacy MT MySQL database. (Default)",
        ),
    )
    args = ""
    help = "Imports Events from legacy MT MySQL database."

    def handle(self, *args, **options):

        db = MySQLdb.connect(
            host=settings.MT_MYSQL_DB_HOST,
            user=settings.MT_MYSQL_DB_USER,
            passwd=settings.MT_MYSQL_DB_PASSWORD,
            db=settings.MT_MYSQL_DB_NAME,
            charset="utf8",
            use_unicode=True,
        )
        cur = db.cursor(MySQLdb.cursors.DictCursor)

        # FETCH THE EVENTS.

        cur.execute(
            "SELECT id, event_text, event_url, event_date, "
            "event_source "
            "FROM pepys_event"
        )

        rows = cur.fetchall()
        count = 0
        for row in rows:
            if count % 100 == 0:
                print(count)

            if row["event_date"] is None:
                print("Invalid Date (ID %s): %s" % (row["id"], row["event_date"]))
            else:
                sources = {
                    "gadbury": DayEvent.GADBURY_CHOICE,
                    "parliament": DayEvent.PARLIAMENT_CHOICE,
                    "earlscolne": DayEvent.JOSSELIN_CHOICE,
                }

                event = DayEvent(
                    id=row["id"],
                    title=row["event_text"],
                    url=row.get("event_url", ""),
                    event_date=row["event_date"],
                    source=sources[row["event_source"]],
                )
                event.save()
                count += 1

        cur.close()
        db.close()
