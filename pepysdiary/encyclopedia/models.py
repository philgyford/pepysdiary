#! -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, pre_delete
from django.urls import reverse

from django_comments.moderation import CommentModerator, moderator
from markdown import markdown
from treebeard.mp_tree import MP_Node, MP_NodeManager

from pepysdiary.common.models import PepysModel
from pepysdiary.encyclopedia.managers import TopicManager
from pepysdiary.encyclopedia import category_lookups
from pepysdiary.encyclopedia import topic_lookups


class Topic(PepysModel):

    # These are inherited from Movable Type data, but I'm not sure we
    # actually use them...
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
    wikipedia_html = models.TextField(blank=True, null=False,
        help_text="Will be populated automatically.")
    wikipedia_last_fetch = models.DateTimeField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='encyclopedia/thumbnails',
        blank=True, null=True, help_text="100 x 120 pixels")
    on_pepys_family_tree = models.BooleanField(blank=False, null=False,
        verbose_name='Is on the Pepys family tree?', default=False)
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    map_category = models.CharField(max_length=20, blank=True, null=False,
                                choices=MAP_CATEGORY_CHOICES, db_index=True,
                                help_text="(UNUSED?) The type of object this is on maps")
    latitude = models.DecimalField(max_digits=11, decimal_places=6,
                                                        blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=6,
                                                        blank=True, null=True)
    zoom = models.SmallIntegerField(blank=True, null=True)
    shape = models.TextField(blank=True, null=False,
        help_text="Lat/long coordinate pairs, separated by semicolons, eg '51.513558,-0.104268;51.513552,-0.104518;...', from http://www.birdtheme.org/useful/v3largemap.html (formatted slightly differently).")

    categories = models.ManyToManyField('Category', related_name='topics')

    diary_references = models.ManyToManyField('diary.Entry', related_name='topics')
    letter_references = models.ManyToManyField('letters.Letter', related_name='topics')

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    comment_name = 'annotation'

    # Keeps track of whether we've made the order_title for this model yet.
    _order_title_made = False
    _original_categories_pks = []

    objects = TopicManager()

    class Meta:
        ordering = ['order_title', ]

    def __str__(self):
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

    @property
    def has_location(self):
        """Do we have lat/long for this topic?"""
        if self.latitude is not None and self.longitude is not None:
            return True
        else:
            return False

    @property
    def has_polygon(self):
        """Do we have shape data, and does it describe a complete polygon?"""
        if self.shape == '':
            return False
        else:
            points = self.shape.split(';')
            if points[0] == points[-1]:
                return True
            else:
                return False

    @property
    def has_path(self):
        """Do we have shape data, and does it describe a path (eg, a road)?"""
        if self.shape == '':
            return False
        else:
            points = self.shape.split(';')
            if points[0] == points[-1]:
                return False
            else:
                return True

    @property
    def category_map_id(self):
        """
        If this Topic is in a Category that has a category map, then this
        returns the ID of that Category.
        Otherwise, returns None.
        """
        valid_map_category_ids = Category.objects.valid_map_category_ids()
        for category in self.categories.all():
            if category.id in valid_map_category_ids:
                return category.id
        return None

    def make_order_title(self):
        """
        Set the order_title, depending on what type of Topic this is.
        """
        try:
            people_category = Category.objects.get(pk=settings.PEOPLE_CATEGORY_ID)
        except Category.DoesNotExist:
            people_category = None
        if people_category is not None and people_category in self.categories.all():
            self.order_title = Topic.objects.make_order_title(
                                                self.title, is_person=True)
        else:
            self.order_title = Topic.objects.make_order_title(
                                            self.title, is_person=False)

    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={'pk': self.pk, })

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return {
            'A': self.title,
            'B': self.summary,
            'B': self.wheatley,
        }

    def get_annotated_diary_references(self):
        """
        Returns a list of lists, of this Topic's diary entry references.
        Doesn't include years/months where there are no referring Entries.
        [
            ['1660', [
                'Jan', [Entry, Entry, Entry, ],
                'Mar', [Entry, Entry, ],
            ]],
            ['1663', [
                'Dec', [Entry, ],
            ],
            ...
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

    # Useful in the templates:

    @property
    def wikipedia_url(self):
        if self.wikipedia_fragment:
            return 'https://en.wikipedia.org/wiki/{}'.format(self.wikipedia_fragment)
        else:
            return ''

    @property
    def is_family_tree(self):
        return self.id == topic_lookups.FAMILY_TREE

    @property
    def is_person(self):
        """
        If at least one of this topic's categories is directly within People,
        then True. All people topics are direct descendants of People category.
        """
        for c in self.categories.all():
            if c.id == category_lookups.PEOPLE:
                return True
        return False

    @property
    def is_place(self):
        """
        If this Topic is somewhere beneath the Places top-level category, then
        true, else false.
        """
        for c in self.categories.all():
            if c.get_root().id == category_lookups.PLACES:
                return True
        return False


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


class CategoryManager(MP_NodeManager):
    def map_category_choices(self):
        """
        The categories we DO use on the maps page.
        As opposed to the Topic.map_category, which appears to be unused.
        This structure is used to generate the SELECT field on the
        /encyclopedia/map/ page.
        The numbers are the IDs of the relevant Categories.

        To add a new option to the map, you should ONLY need to add it to
        this structure, and everything else should work...
        You might also want to adjust the start_coords in pepys.js if the map
        should be focused on something other than central London.
        """
        return (
            ('London', (
                (category_lookups.PLACES_LONDON_AREAS,          'Areas of London'),
                (category_lookups.PLACES_LONDON_CHURCHES,       'Churches and cathedrals in London'),
                (category_lookups.PLACES_LONDON_GOVERNMENT,     'Government buildings'),
                (category_lookups.PLACES_LONDON_LIVERY_HALLS,   'Livery halls'),
                (category_lookups.PLACES_LONDON_STREETS,        'Streets, gates, squares, piers, etc'),
                (category_lookups.PLACES_LONDON_TAVERNS,        'Taverns in London'),
                (category_lookups.PLACES_LONDON_THEATRES,       'Theatres in London'),
                (category_lookups.PLACES_LONDON_WHITEHALL,      'Whitehall Palace'),
                (category_lookups.PLACES_LONDON_ROYAL,          'Other royal buildings'),
                (category_lookups.PLACES_LONDON_OTHER,          'Other London buildings'),
            ), ),
            (category_lookups.PLACES_LONDON_ENVIRONS,       'London environs'),
            (category_lookups.PLACES_BRITAIN_WATERWAYS,     'Waterways in Britain'),
            (category_lookups.PLACES_BRITAIN_REST,          'Rest of Britain'),
            (category_lookups.PLACES_WORLD_REST,            'Rest of the world'),
        )

    def valid_map_category_ids(self):
        """
        Returns a list of the category IDs in map_category_choices().
        Assumes we only have one sub-level.
        There's probably some clever one-line way of doing this, but still.
        """
        choices = self.map_category_choices()
        ids = []
        for tup1 in choices:
            if isinstance(tup1[0], int):
                ids.append(tup1[0])
            else:
                for tup2 in tup1[1]:
                    ids.append(tup2[0])
        return ids


class Category(MP_Node):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=50, blank=False, null=False)
    topic_count = models.IntegerField(default=0, blank=False, null=False)

    # Will also have a `topics` field, listing Topics within the Category.

    objects = CategoryManager()

    node_order_by = ['title', ]

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
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
