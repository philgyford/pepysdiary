# coding: utf-8
import MySQLdb
from optparse import make_option
import pytz

from django.conf import settings
from django.core.management.base import BaseCommand

from pepysdiary.common.utilities import fix_old_links
from pepysdiary.diary.models import Entry

# You'll need to: pip install MySQL-python


class Command(BaseCommand):
    """
    Gets all the Diary Entries from the MovableType MySQL database and
    creates a new Django object for each one.

    References to Encyclopedia Topics will be created by the Topic model.

    Usage:
    $ ./manage.py import_mt_entries

    And afterwards, do this:
    $ ./manage.py sqlsequencereset 'diary'
    and run the SQL commands it gives you.
    """

    option_list = BaseCommand.option_list + (
        make_option(
            "--all",
            action="store_true",
            dest="all",
            default=True,
            help="Import all Diary Entries from legacy MT MySQL database. (Default)",
        ),
    )
    args = ""
    help = "Imports Diary Entries from legacy MT MySQL database."

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

        # FETCH THE DIARY ENTRIES.

        cur.execute(
            "SELECT entry_id, entry_title, entry_text, "
            "entry_text_more, entry_created_on, entry_authored_on "
            "FROM mt_entry WHERE entry_blog_id='%s'" % (settings.MT_DIARY_BLOG_ID)
        )

        rows = cur.fetchall()
        for row in rows:
            print("%s %s" % (row["entry_id"], row["entry_title"]))

            # Fix any old-style links in the two text fields.
            if row["entry_text"] is None:
                text = ""
            else:
                text = fix_old_links(row["entry_text"])
            if row["entry_text_more"] is None:
                footnotes = ""
            else:
                footnotes = fix_old_links(row["entry_text_more"])

            entry = Entry(
                id=row["entry_id"],
                title=row["entry_title"],
                text=text,
                footnotes=footnotes,
                diary_date=row["entry_authored_on"],
            )
            entry.save()

            # SET ORIGINAL CREATED TIME.
            created_time = row["entry_created_on"].replace(tzinfo=pytz.utc)
            entry.date_created = created_time
            entry.save()

        cur.close()
        db.close()
