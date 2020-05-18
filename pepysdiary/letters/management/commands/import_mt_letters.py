# coding: utf-8
import MySQLdb
from optparse import make_option
import pytz
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from pepysdiary.common.utilities import fix_old_links
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.letters.models import Letter

# You'll need to: pip install MySQL-python


class Command(BaseCommand):
    """
    Gets all the Letters from the MovableType MySQL database and
    creates a new Django object for each one.

    References to Encyclopedia Topics will be created by the Topic model.

    Usage:
    $ ./manage.py import_mt_letters

    And afterwards, do this:
    $ ./manage.py sqlsequencereset 'letters'
    and run the SQL commands it gives you.
    """

    option_list = BaseCommand.option_list + (
        make_option(
            "--all",
            action="store_true",
            dest="all",
            default=True,
            help="Import all Letters from legacy MT MySQL database. (Default)",
        ),
    )
    args = ""
    help = "Imports Letters from legacy MT MySQL database."

    def handle(self, *args, **options):

        # Because there aren't many senders/recipients, a semi-manual lookup
        # of name -> Topic ID.
        people = {
            "Anthony Deane": 5132,
            "Balthazar St Michel": 631,
            "the Brooke House Commissioners": 12029,
            "Capt. Thomas Elliot": 10002,
            "Charles II": 344,
            "Col. Thomas Middleton": 7120,
            "Henry Savile": 9425,
            "James Southerne": 977,
            "John Evelyn": 1033,
            "John Pepys (brother)": 117,
            "Lord Henry Howard": 10586,
            "Matthew Wren": 8019,
            "Samuel Pepys": 29,
            "Sir Richard Browne": 3795,
            "Thomas Hill": 7165,
            "Thomas Povey": 5263,
        }

        db = MySQLdb.connect(
            host=settings.MT_MYSQL_DB_HOST,
            user=settings.MT_MYSQL_DB_USER,
            passwd=settings.MT_MYSQL_DB_PASSWORD,
            db=settings.MT_MYSQL_DB_NAME,
            charset="utf8",
            use_unicode=True,
        )
        cur = db.cursor(MySQLdb.cursors.DictCursor)

        # 1) FETCH THE LETTERS.

        cur.execute(
            "SELECT entry_id, entry_title, entry_text, "
            "entry_text_more, entry_excerpt, entry_basename, "
            "entry_created_on, entry_authored_on "
            "FROM mt_entry WHERE entry_blog_id='%s'" % (settings.MT_LETTERS_BLOG_ID)
        )

        rows = cur.fetchall()
        for row in rows:
            print("%s %s" % (row["entry_id"], row["entry_title"]))

            # 2) Fix any old-style links in the two text fields.
            if row["entry_text"] is None:
                text = ""
            else:
                text = fix_old_links(row["entry_text"])
            if row["entry_text_more"] is None:
                footnotes = ""
            else:
                footnotes = fix_old_links(row["entry_text_more"])

            # 3) Create initial object, but don't save yet.
            letter = Letter(
                id=row["entry_id"],
                title=row["entry_title"],
                text=text,
                footnotes=footnotes,
                excerpt=row["entry_excerpt"],
                slug=row["entry_basename"],
                letter_date=row["entry_authored_on"],
            )

            # 4) FETCH AND ADD CUSTOM FIELDS.

            cur.execute(
                "SELECT entry_meta_type, entry_meta_vchar_idx "
                "FROM mt_entry_meta WHERE "
                "entry_meta_entry_id='%s'" % (row["entry_id"])
            )
            meta_rows = cur.fetchall()

            for meta_row in meta_rows:
                if (
                    meta_row["entry_meta_type"] == "field.display_date"
                    and meta_row["entry_meta_vchar_idx"] != ""
                ):
                    letter.display_date = meta_row["entry_meta_vchar_idx"]

                if meta_row["entry_meta_type"] == "field.letter_source":
                    if meta_row["entry_meta_vchar_idx"] == "Guy de la Bédoyère":
                        letter.source = Letter.GUY_DE_LA_BEDOYERE_SOURCE
                    elif meta_row["entry_meta_vchar_idx"] == "Helen Truesdell Heath":
                        letter.source = Letter.HELEN_TRUESDELL_HEATH_SOURCE

            # 5) Work out sender/recipient from title.
            # (We don't bother with the old MT categories; too complicated, and
            # not many of them.)
            # Very cavalier, no error checking.
            title_matches = re.match(r"^(.*?)\sto\s(.*?)$", row["entry_title"]).groups()
            letter.sender = Topic.objects.get(pk=people[title_matches[0]])
            letter.recipient = Topic.objects.get(pk=people[title_matches[1]])

            letter.save()

            # SET ORIGINAL CREATED TIME.
            created_time = row["entry_created_on"].replace(tzinfo=pytz.utc)
            letter.date_created = created_time
            letter.save()

        cur.close()
        db.close()
