import re

from django.conf import settings
from django.contrib.comments.moderation import CommentModerator, moderator
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, pre_delete

from markdown import markdown
from treebeard.mp_tree import MP_Node

from pepysdiary.common.models import PepysModel


class TopicManager(models.Manager):
    def make_order_title(self, text, is_person=False):
        """
        If is_person we change:

        "Fred Bloggs" to "Bloggs, Fred"
        "Sidney Smythe (1st Lord Smythe)" to "Smythe, Sidney (1st Lord Smythe)"
        "Sir Heneage Finch (Solicitor-General)" to "Finch, Sir Heneage (Solicitor-General)"
        "Capt. Henry Terne" to "Terne, Capt. Henry"
        "Capt. Aldridge" to "Aldridge, Capt."
        "Mr Hazard" to "Hazard, Mr"
        "Johann Heinrich Alsted" to "Alsted, Johann Heinrich"
        "Monsieur d'Esquier" to "Esquier, Monsieur d'"
        "Adriaen de Haes" to "Haes, Adriaen de"
        "Jan de Witt (Grand Pensionary of Holland)" to "Witt, Jan de (Grand Pensionary of Holland)"
        "Peter de la Roche" to "Roche, Peter de la"
        "Monsieur du Prat" to "Prat, Monsieur du"
        "Catherine of Braganza (Queen)" to "Braganza, Catherine of (Queen)"
        "Michiel van Gogh (Dutch Ambassador, 1664-5)" to "Gogh, Michiel van (Dutch Ambassador, 1664-5)"

        Stay the same:
        "Mary (c, Pepys' chambermaid)"
        "Shelston"
        "Mary I of England"
        "Philip IV (King of Spain, 1621-1665)"
        "Ivan the Terrible"

        If not is_person we change:
        "The Royal Prince" to "Royal Prince, The"
        "The Alchemist (Ben Jonson)" to "Alchemist, The (Ben Jonson)"
        """
        order_title = text

        if is_person:
            # First we take off any bit in parentheses at the end.
            name_match = re.match(r'^(.*?)(?:\s)?(\(.*?\))?$', text)
            parentheses = ''
            if name_match is not None:
                matches = name_match.groups()
                if matches[1] is not None:
                    parentheses = ' %s' % matches[1]
                # The actual name part of the string:
                name = matches[0]

            pattern = """
                # Optionally match a title:
                (Ald\.|Capt\.|Col\.|Don|Dr|Lady|Lieut\.|Lord|Lt-Adm\.|Lt-Col\.|Lt-Gen\.|Maj\.(?:-Gen\.)?(?:\sAld\.)?(?:\sSir)?|Miss|(?:Mrs?)|Ms|Pope|Sir)?
                # Ignore any space after a title:
                (?:\s)?
                # Match a single first name:
                (.*?)
                # Match any other names up until the end:
                (?:\s(.*?))?
                # That's it:
                $
            """
            name_match = re.match(pattern, name, re.VERBOSE)
            if name_match is None:
                # Leave it as it is.
                pass
            else:
                matches = list(name_match.groups())

                # We need to trap anything that's like:
                # "Mary I of England"
                # "Philip IV (King of Spain, 1621-1665)"
                # "Ivan the Terrible"
                king_match = None
                if matches[2] is not None:
                    king_match = re.match(r'^(I|II|III|IV|V|VI|VII|VIII|XI|XIV|the)(?:\s|$)',
                                                                    matches[2])
                if king_match is not None:
                    # Looks like it's a king-type person.
                    # Leave the text as it was.
                    pass
                else:
                    # Save any title, plus a space, or just nothing:
                    title = ''
                    if matches[0] is not None:
                        title = '%s ' % matches[0]

                    if matches[2] is not None:
                        # The "surname" part has something in it.

                        if matches[2][:1] == '(':
                            # eg, (None, 'Mary', "(c, Pepys' chambermaid)", None)
                            # leave it as-is.
                            pass
                        elif matches[1][-1:] == ',':
                            # eg, (None, 'Godefroy,', "Comte d'Estrades")
                            # leave it as-is.
                            pass
                        else:
                            # A little fix first for surnames like "d'Esquier".
                            # We want to move any leading "d'" or "l'" from the
                            # start of the surname to the end of the first names.
                            # So that we'll order by "Esquier".
                            apostrophe_match = re.match(r"^(d'|l'|al-)(.*?)$", matches[2])
                            if apostrophe_match is not None:
                                # Will be something like ("d'", "Esquier"):
                                apostrophe_matches = apostrophe_match.groups()
                                # Will be like "Monsieur d'":
                                matches[1] = '%s %s' % (matches[1], apostrophe_matches[0])
                                # Will be like "Esquier":
                                matches[2] = apostrophe_matches[1]

                            # See what's in the "surname" part.
                            # One word or more?
                            surname_match = re.match(
                                                r'^(.*)(?:\s)(.*?)$', matches[2])
                            if surname_match is None:
                                # "surname" was just one word, simple.
                                # eg, (None, 'Fred', 'Bloggs', None)
                                order_title = '%s, %s%s%s' % (matches[2], title,
                                                        matches[1], parentheses)
                            else:
                                # "surname" has more than one word.
                                # eg, (None, 'Adriaen', 'de Haes', None)
                                surname_matches = surname_match.groups()
                                # surname_matches might now be like:
                                # ('de la', 'Roche')
                                pre_surname = ''
                                if surname_matches[0]:
                                    pre_surname = ' %s' % surname_matches[0]
                                order_title = '%s, %s%s%s%s' % (surname_matches[1],
                                        title, matches[1], pre_surname, parentheses)
                    elif title != '':
                        # eg, ('Mr', 'Hazard', None)
                        # Need to remove extra space from title, eg 'Mr ':
                        order_title = '%s, %s' % (matches[1], title[:-1])
                    else:
                        pass

        else:
            the_pattern = re.compile(r'^The\s(.*?)(?:\s\((.*?)\))?$')
            the_match = the_pattern.match(text)
            if the_match is not None:
                # Starts with 'The '.
                matches = the_match.groups()
                if matches[1] is None:
                    # eg, ('Royal Prince', None)
                    order_title = '%s, The' % matches[0]
                else:
                    # eg, ('Alchemist', 'Ben Jonson')
                    order_title = '%s, The (%s)' % (matches[0], matches[1])

        return order_title


class Topic(PepysModel):

    MAP_CATEGORY_AREA = 'area'
    MAP_CATEGORY_GATE = 'gate'
    MAP_CATEGORY_HOME = 'home'
    MAP_CATEGORY_MISC = 'misc'
    MAP_CATEGORY_ROAD = 'road'
    MAP_CATEGORY_STAIR = 'stair'
    MAP_CATEGORY_TOWN = 'town'
    MAP_CATEGORY_CHOICES = (
        (MAP_CATEGORY_AREA, 'Area'),
        (MAP_CATEGORY_GATE, 'Gate'),
        (MAP_CATEGORY_HOME, "Pepys' home(s)"),
        (MAP_CATEGORY_MISC, 'Misc'),
        (MAP_CATEGORY_ROAD, 'Road/Street'),
        (MAP_CATEGORY_STAIR, 'Stair/Pier'),
        (MAP_CATEGORY_TOWN, 'Town/Village'),
    )

    title = models.CharField(max_length=255, blank=False, null=False)
    order_title = models.CharField(max_length=255, blank=True, null=False)
    summary = models.TextField(blank=True, null=False,
                                                help_text="Can use Markdown.")
    summary_html = models.TextField(blank=True, null=False,
        help_text="The summary field, with Markdown etc, turned into HTML.")
    wheatley = models.TextField(blank=True, null=False,
        help_text="Can use Markdown. Taken from footnotes in the 1893 Wheatley edition of the diary.")
    wheatley_html = models.TextField(blank=True, null=False,
        help_text="The wheatley field, with Markdown etc, turned into HTML.")
    tooltip_text = models.TextField(blank=True, null=False,
                        help_text="For hovering over links in diary entries.")
    wikipedia_fragment = models.CharField(
        max_length=255, blank=True, null=False,
        help_text="From the Wikipedia page URL, if any, eg, 'Samuel_Pepys'.")
    thumbnail = models.ImageField(upload_to='encyclopedia/thumbnails',
        blank=True, null=True, help_text="100 x 120 pixels")
    on_pepys_family_tree = models.BooleanField(blank=False, null=False,
        verbose_name='Is on the Pepys family tree?', default=False)
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    map_category = models.CharField(max_length=20, blank=True, null=False,
                                choices=MAP_CATEGORY_CHOICES,
                                help_text="The type of object this is on maps")
    latitude = models.DecimalField(max_digits=11, decimal_places=6,
                                                        blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=6,
                                                        blank=True, null=True)
    zoom = models.SmallIntegerField(blank=True, null=True)
    shape = models.TextField(blank=True, null=False,
        help_text="Lat/long coordinate pairs, separated by semicolons, eg '51.513558,-0.104268;51.513552,-0.104518;...', from http://www.birdtheme.org/useful/googletoollargemap.html (formatted slightly differently).")

    categories = models.ManyToManyField('Category', related_name='topics')

    diary_references = models.ManyToManyField('diary.Entry', related_name='topics')
    letter_references = models.ManyToManyField('letters.Letter', related_name='topics')

    comment_name = 'annotation'

    # Keeps track of whether we've made the order_title for this model yet.
    _order_title_made = False
    _original_categories_pks = []

    objects = TopicManager()

    class Meta:
        ordering = ['order_title', ]

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.summary_html = markdown(self.summary)
        self.wheatley_html = markdown(self.wheatley)
        super(Topic, self).save(*args, **kwargs)

        if self._order_title_made == False:
            # When importing data we need to do the make_order_title() after
            # we've saved the model, and its category ManyToMany field, but
            # we don't want to get into an infinite loop. So this makes sure
            # we only save the model one extra time:
            self.make_order_title()
            self._order_title_made = True
            self.save()
            for cat in self.categories.all():
                cat.set_topic_count()
            self._order_title_made = False

    def make_order_title(self):
        """
        Set the order_title, depending on what type of Topic this is.
        """
        people_category = Category.objects.get(pk=settings.PEOPLE_CATEGORY_ID)
        if people_category in self.categories.all():
            self.order_title = Topic.objects.make_order_title(
                                                self.title, is_person=True)
        else:
            self.order_title = Topic.objects.make_order_title(
                                            self.title, is_person=False)

    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={'pk': self.pk, })

    def get_annotated_diary_references(self):
        """
        Returns a list of lists, of this Topic's diary entry references.
        [
            ['1660', [
                'Jan', [Entry, Entry, Entry, ],
                'Feb', [Entry, Entry, ],
            ]],
        ]
        """
        refs = []
        year_refs = []
        month_refs = []
        prev_year = None
        prev_yearmonth = None
        for ref in self.diary_references.order_by('diary_date'):
            if ref.year + ref.month_b != prev_yearmonth:
                if prev_yearmonth is not None:
                    year_refs[1].append(month_refs)
                month_refs = [ref.month_b, []]
            if ref.year != prev_year:
                if prev_year is not None:
                    refs.append(year_refs)
                year_refs = [ref.year, []]
            month_refs[1].append(ref)
            prev_year = ref.year
            prev_yearmonth = ref.year + ref.month_b
        if len(year_refs) > 0:
            year_refs[1].append(month_refs)
            refs.append(year_refs)
        return refs


class TopicModerator(CommentModerator):
    email_notification = False
    enable_field = 'allow_comments'

moderator.register(Topic, TopicModerator)


def topic_categories_changed(sender, **kwargs):
    """
    When we add or remove categories on this topic, we need to re-set those
    categories' topic counts.
    """
    if kwargs['reverse'] == False:
        # We're changing the categories on a topic.
        if kwargs['action'] == 'pre_clear':
            # Before we do anything,
            # store the PKs of the current categories on this topic.
            kwargs['instance']._original_categories_pks = [
                            c.pk for c in kwargs['instance'].categories.all()]

        elif kwargs['action'] in ['post_add', 'post_remove']:
            # Finished the action, so now change the old and new categories'
            # topic counts.
            # The PKs of the categories the topic has now:
            new_pks = kwargs.get('pk_set', [])
            # Make a list of both the new and old categories' PKs:
            pks = kwargs['instance']._original_categories_pks + list(
                set(new_pks) - set(kwargs['instance']._original_categories_pks))
            # For all the old and new categories, set the counts:
            for pk in pks:
                cat = Category.objects.get(pk=pk)
                cat.set_topic_count()
    else:
        # We're changing a Category's topics, so set that Category's count.
        if kwargs['instance'] is not None:
            kwargs['instance'].set_topic_count()

m2m_changed.connect(topic_categories_changed, sender=Topic.categories.through)


def topic_pre_delete(sender, **kwargs):
    """
    Before deleting the topic, store the categories it has so that...
    """
    kwargs['instance']._original_categories_pks = [
                            c.pk for c in kwargs['instance'].categories.all()]

pre_delete.connect(topic_pre_delete, sender=Topic)


def topic_post_delete(sender, **kwargs):
    """
    ...after deleting the topic, we re-set its categories' topic counts.
    """
    for pk in kwargs['instance']._original_categories_pks:
        cat = Category.objects.get(pk=pk)
        cat.set_topic_count()

post_delete.connect(topic_post_delete, sender=Topic)


class Category(MP_Node):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=50, blank=False, null=False)
    topic_count = models.IntegerField(default=0, blank=False, null=False)

    # Will also have a `topics` field, listing Topics within the Category.

    node_order_by = ['title', ]

    class Meta:
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return '%s' % self.title

    def get_absolute_url(self):
        # Join all the parent categories' slugs, eg:
        # 'fooddrink/drink/alcdrinks'.
        parent_slugs = '/'.join([c.slug for c in self.get_ancestors()])
        if parent_slugs:
            path = '%s/%s' % (parent_slugs, self.slug)
        else:
            # Top level category.
            path = '%s' % self.slug
        return reverse('category_detail', kwargs={'slugs': path, })

    def set_topic_count(self):
        """
        Should be called when we add/delete a Topic.
        Just means we don't have to do the count() query live whenever we
        want to display the number in templates.
        """
        self.topic_count = self.topics.count()
        self.save()
