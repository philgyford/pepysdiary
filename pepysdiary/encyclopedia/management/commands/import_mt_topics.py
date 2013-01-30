# coding: utf-8
import MySQLdb
from optparse import make_option
import pytz
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from pepysdiary.common.utilities import fix_old_links
from pepysdiary.encyclopedia.models import Category, Topic


# You'll need to: pip install MySQL-python

# NOTE:
# After running this, I added the `on_pepys_family_tree` field, and ran this
# query to update the Topics:
# UPDATE encyclopedia_topic SET on_pepys_family_tree='t' WHERE id IN (112, 114, 115, 116, 116, 117, 119, 120, 121, 150, 154, 171, 236, 247, 282, 342, 507, 563, 569, 612, 631, 670, 671, 676, 749, 750, 850, 884, 911, 915, 951, 972, 995, 1066, 1067, 1090, 1105, 1107, 1342, 1558, 1568, 1593, 1650, 1709, 1749, 1761, 1858, 1858, 2226, 2531, 2542, 2724, 2725, 2802, 2803, 2807, 2848, 2930, 2931, 2934, 2998, 3002, 3003, 3065, 3286, 3690, 3735, 3736, 4212, 4213, 5137, 5180, 5265, 5516, 5735, 6232, 6750, 6763, 6764, 7192, 7231, 7294, 7392, 7436, 7721, 8086, 8250, 8544, 8988, 8989, 8990, 11061, 12615, 12989, 13006, 13169, 13281, 13282, 13648, 13845);

class Command(BaseCommand):
    """
    Gets all the Encyclopedia Topics from the MovableType MySQL database and
    creates a new Django object for each one.

    Doesn't do comments or the references to Diary Entries.

    Usage:
    $ ./manage.py import_mt_topics

    And afterwards, do this:
    $ ./manage.py sqlsequencereset 'encyclopedia'
    and run the SQL commands it gives you.
    """
    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=True,
            help="Import all Encyclopedia Topics from legacy MT MySQL database. (Default)"),
    )
    args = ''
    help = "Imports Encyclopedia Topics from legacy MT MySQL database."

    def handle(self, *args, **options):

        # 1) SET UP INITIAL STUFF.

        valid_map_categories = [k for (k, v) in Topic.MAP_CATEGORY_CHOICES]

        # Used to match things like:
        # 'Alchemist, The (Ben Jonson)' or 'Royal Prince, The'
        # so that we can move 'The' to the start of the title.
        title_pattern = re.compile(r'^(.*?),\sThe(?:\s|$)(.*)$')

        # Used to match things like:
        # 'Bloggs, Fred', so it can change to 'Fred Bloggs'
        # 'Smythe, Sidney (1st Lord Smythe)' to 'Sidney Smythe (1st Lord Smythe)'
        # but "Mary (c, Pepys' chambermaid)" will remain the same.
        name_pattern = re.compile(r'(.*?)(?:,\s(.*?))?(?:\s\((.*?)\))?$')

        # The category that all people have, so we know to fix their names.
        people_category = Category.objects.get(pk=2)

        db = MySQLdb.connect(host=settings.MT_MYSQL_DB_HOST,
                            user=settings.MT_MYSQL_DB_USER,
                            passwd=settings.MT_MYSQL_DB_PASSWORD,
                            db=settings.MT_MYSQL_DB_NAME,
                            charset='utf8',
                            use_unicode=True)
        cur = db.cursor(MySQLdb.cursors.DictCursor)

        # 2) FETCH THE BASIC ENTRY DATA.

        cur.execute("SELECT entry_id, entry_category_id, entry_title, "
            "entry_excerpt, entry_text, entry_text_more, entry_created_on "
            "FROM mt_entry WHERE entry_blog_id='%s' " % (
                                            settings.MT_ENCYCLOPEDIA_BLOG_ID))

        rows = cur.fetchall()
        for row in rows:
            print '%s %s' % (row['entry_id'], row['entry_title'])

            # 3) CREATE BASIC TOPIC.

            # If the MT title has ", The" in it, move "The" to the front:
            title_match = title_pattern.search(row['entry_title'])
            if title_match is None:
                # Nothing special to do.
                title = row['entry_title']
            else:
                # Need to move 'The' to the start.
                title = 'The ' + title_match.groups()[0]
                if title_match.groups()[1] != '':
                    title += ' ' + title_match.groups()[1]

            # Fix any old-style links.
            if row['entry_text'] is None:
                summary = u''
            else:
                summary = fix_old_links(row['entry_text'])
            if row['entry_text_more'] is None:
                wheatley = u''
            else:
                wheatley = fix_old_links(row['entry_text_more'])
            if row['entry_excerpt'] is None:
                tooltip_text = ''
            else:
                tooltip_text = row['entry_excerpt']

            topic = Topic(id=row['entry_id'],
                        title=title,
                        order_title=row['entry_title'],
                        summary=summary,
                        wheatley=wheatley,
                        tooltip_text=tooltip_text
                        )

            # 4) FETCH AND ADD CUSTOM FIELDS.

            # latitude, longitude, map_category, wikipedia_title and zoom are
            # stored in entry_meta_vchar_idx.
            # shape is stored in entry_meta_vclob
            # Image is indicated by '1' in entry_meta_vinteger_idx.
            cur.execute("SELECT entry_meta_type, entry_meta_vchar_idx, "
                        "entry_meta_vclob, entry_meta_vinteger_idx "
                        "FROM mt_entry_meta WHERE "
                        "entry_meta_entry_id='%s'" % (row['entry_id']))
            meta_rows = cur.fetchall()
            for meta_row in meta_rows:
                if meta_row['entry_meta_type'] == 'field.latitude' and \
                    meta_row['entry_meta_vchar_idx'] != '':
                    topic.latitude = meta_row['entry_meta_vchar_idx']

                if meta_row['entry_meta_type'] == 'field.longitude' and \
                    meta_row['entry_meta_vchar_idx'] != '':
                    topic.longitude = meta_row['entry_meta_vchar_idx']

                if meta_row['entry_meta_type'] == 'field.map_category' and \
                    meta_row['entry_meta_vchar_idx'] != '':
                    if meta_row['entry_meta_vchar_idx'] in valid_map_categories:
                        topic.map_category = meta_row['entry_meta_vchar_idx']
                    elif meta_row['entry_meta_vchar_idx'] != 'none':
                        print "INVALID MAP CATEGORY: '%s' for Entry ID '%s'" % (
                            meta_row['entry_meta_vchar_idx'], row['entry_id'])

                if meta_row['entry_meta_type'] == 'field.wikipedia_title' and \
                    meta_row['entry_meta_vchar_idx'] != '':
                    topic.wikipedia_fragment = meta_row['entry_meta_vchar_idx']

                if meta_row['entry_meta_type'] == 'field.zoom' and \
                    meta_row['entry_meta_vchar_idx'] != '':
                    topic.zoom = meta_row['entry_meta_vchar_idx']

                if meta_row['entry_meta_type'] == 'field.shape' and \
                    meta_row['entry_meta_vclob'] != '':
                    topic.shape = meta_row['entry_meta_vclob']

            topic.save()

            # 5) ADD THUMBNAIL IMAGE (must be done after save()).

            for meta_row in meta_rows:
                if meta_row['entry_meta_type'] == 'field.thumbnail_image' and \
                    meta_row['entry_meta_vinteger_idx'] == 1:
                    topic.thumbnail = 'encyclopedia/thumbnails/%s.jpg' % (
                                                                    topic.pk)
                    topic.save()

            # 6) FETCH AND ADD CATEGORIES.

            cur.execute("SELECT placement_category_id FROM mt_placement "
                        "WHERE placement_entry_id='%s'" % (row['entry_id']))
            cat_rows = cur.fetchall()
            for cat_row in cat_rows:
                try:
                    category = Category.objects.get(
                                        pk=cat_row['placement_category_id'])
                    topic.categories.add(category)
                except Category.DoesNotExist:
                    print "INVALID CATEGORY ID: '%s' for Entry ID '%s'" % (
                        cat_row['placement_category_id'], row['entry_id'])

            # 7) TIDY UP NAMES OF PEOPLE.

            if people_category in topic.categories.all():
                name_match = name_pattern.search(topic.title)
                if name_match.groups() is not None:
                    matches = name_match.groups()
                    if matches[1] is None:
                        # eg, "Mary (c, Pepys' chambermaid)".
                        # No surname, so leave it alone.
                        pass
                    elif matches[2] is not None:
                        # eg, 'Smythe, Sidney (1st Lord Smythe)'
                        # becomes 'Sidney Smythe (1st Lord Smythe)',
                        topic.title = '%s %s (%s)' % (matches[1],
                                                    matches[0],
                                                    matches[2])
                    else:
                        # eg, 'Bloggs, Fred' becomes 'Fred Bloggs'.
                        topic.title = '%s %s' % (matches[1], matches[0])
                    # We would topic.save() here, but we do it below after
                    # setting date_created, so no need to do it twice.

            # 8) SET ORIGINAL CREATED TIME.

            created_time = row['entry_created_on'].replace(tzinfo=pytz.utc)
            topic.date_created = created_time
            topic.save()

        cur.close()
        db.close()
