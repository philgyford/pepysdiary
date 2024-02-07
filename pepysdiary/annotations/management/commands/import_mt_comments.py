import re
from datetime import timezone
from optparse import make_option

import MySQLdb
from django.conf import settings
from django.core.management.base import BaseCommand

from pepysdiary.annotations.models import Annotation
from pepysdiary.common.utilities import fix_old_links

# You'll need to: pip install MySQL-python


class Command(BaseCommand):
    """
    Gets all the Comments from the MovableType MySQL database and
    creates a new Django object for each one.

    Usage:
    $ ./manage.py import_mt_comments

    It might take several hours...

    And afterwards, do this:
    $ ./manage.py sqlsequencereset 'comments'
    and run the SQL commands it gives you.
    """

    option_list = BaseCommand.option_list + (
        make_option(
            "--all",
            action="store_true",
            dest="all",
            default=True,
            help="Import all Comments from legacy MT MySQL database. (Default)",
        ),
    )
    args = ""
    help = "Imports Comments from legacy MT MySQL database."

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

        # FETCH THE COMMENTS.

        sql = (
            "SELECT comment_id, comment_blog_id, comment_entry_id, "
            "comment_ip, comment_author, comment_email, comment_url, "
            "comment_text, comment_created_on, comment_modified_on "
            "FROM mt_comment WHERE comment_visible='1' "
            "AND comment_blog_id IN (%s, %s, %s, %s, %s)"
        )
        cur.execute(
            sql,
            (
                settings.MT_DIARY_BLOG_ID,
                settings.MT_ENCYCLOPEDIA_BLOG_ID,
                settings.MT_IN_DEPTH_BLOG_ID,
                settings.MT_NEWS_BLOG_ID,
                settings.MT_LETTERS_BLOG_ID,
            ),
        )
        rows = cur.fetchall()
        for count, row in enumerate(rows):
            if count % 100 == 0:
                print(count)  # noqa: T201

            # Fix any old-style links in the two text fields.
            if row["comment_text"] is None:
                text = ""
            else:
                text = fix_old_links(row["comment_text"])

            # Remove any <a href...> and </a> HTML:
            text = re.sub(r"<\/?a[^>]*>", "", text)

            if row["comment_blog_id"] == settings.MT_DIARY_BLOG_ID:
                content_type_id = 10
            elif row["comment_blog_id"] == settings.MT_ENCYCLOPEDIA_BLOG_ID:
                content_type_id = 11
            elif row["comment_blog_id"] == settings.MT_IN_DEPTH_BLOG_ID:
                content_type_id = 14
            elif row["comment_blog_id"] == settings.MT_NEWS_BLOG_ID:
                content_type_id = 15
            elif row["comment_blog_id"] == settings.MT_LETTERS_BLOG_ID:
                content_type_id = 13
            else:
                print(  # noqa: T201
                    f"INVALID BLOG ID ({row['comment_blog_id']}) "
                    f"FOR COMMENT ID {row['comment_id']}"
                )

            annotation = Annotation(
                id=row["comment_id"],
                comment=text,
                site_id=1,
                content_type_id=content_type_id,
                object_pk=row["comment_entry_id"],
                user_name=row["comment_author"],
                user_email=row["comment_email"],
                user_url=row["comment_url"],
                ip_address=row["comment_ip"],
                is_public=True,
                submit_date=row["comment_created_on"].replace(tzinfo=timezone.utc),
            )
            annotation.save()

        cur.close()
        db.close()
