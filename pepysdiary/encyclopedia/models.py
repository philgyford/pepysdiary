from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse

from django_comments.moderation import CommentModerator, moderator
from markdown import markdown
from treebeard.mp_tree import MP_Node

from ..common.models import PepysModel
from .managers import CategoryManager, TopicManager
from . import category_lookups
from . import topic_lookups


class Category(MP_Node):
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=50, blank=False, null=False)
    topic_count = models.IntegerField(default=0, blank=False, null=False)

    # Will also have a `topics` field, listing Topics within the Category.

    objects = CategoryManager()

    node_order_by = ["title"]

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        # Join all the parent categories' slugs, eg:
        # 'fooddrink/drink/alcdrinks'.
        parent_slugs = "/".join([c.slug for c in self.get_ancestors()])
        if parent_slugs:
            path = "%s/%s" % (parent_slugs, self.slug)
        else:
            # Top level category.
            path = str(self.slug)
        return reverse("category_detail", kwargs={"slugs": path})

    def set_topic_count(self):
        """
        Should be called when we add/delete a Topic.
        Just means we don't have to do the count() query live whenever we
        want to display the number in templates.
        """
        self.topic_count = self.topics.count()
        self.save()


class Topic(PepysModel):
    class MapCategory(models.TextChoices):
        #  These are inherited from Movable Type data, but I'm not sure we
        # actually use them...
        AREA = "area", "Area"
        GATE = "gate", "Gate"
        HOME = "home", "Pepys' home(s)"
        MISC = "misc", "Miscellaneous"
        ROAD = "road", "Road or Street"
        STAIR = "stair", "Stair or Pier"
        TOWN = "town", "Town or Village"

    title = models.CharField(max_length=255, blank=False, null=False)
    order_title = models.CharField(
        max_length=255, blank=True, null=False, db_index=True
    )
    summary = models.TextField(blank=True, null=False, help_text="Can use Markdown.")
    summary_html = models.TextField(
        blank=True,
        null=False,
        help_text="The summary field, with Markdown etc, turned into HTML.",
    )
    summary_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT,
        related_name="topic_summaries",
        help_text="Optional. Used if Summary Publication Date is set.",
    )
    summary_publication_date = models.DateField(
        blank=True, null=True, help_text="Optional. Used if Summary Author is set."
    )
    wheatley = models.TextField(
        blank=True,
        null=False,
        help_text="Can use Markdown. Taken from footnotes in the 1893 Wheatley "
        "edition of the diary.",
    )
    wheatley_html = models.TextField(
        blank=True,
        null=False,
        help_text="The wheatley field, with Markdown etc, turned into HTML.",
    )
    tooltip_text = models.TextField(
        blank=True, null=False, help_text="For hovering over links in diary entries."
    )
    wikipedia_fragment = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        help_text="From the Wikipedia page URL, if any, eg, 'Samuel_Pepys'.",
    )
    wikipedia_html = models.TextField(
        blank=True, null=False, help_text="Will be populated automatically."
    )
    wikipedia_last_fetch = models.DateTimeField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="encyclopedia/thumbnails",
        blank=True,
        null=True,
        help_text="100 x 120 pixels",
    )
    on_pepys_family_tree = models.BooleanField(
        blank=False,
        null=False,
        verbose_name="Is on the Pepys family tree?",
        default=False,
    )
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    map_category = models.CharField(
        max_length=20,
        blank=True,
        null=False,
        choices=MapCategory.choices,
        db_index=True,
        help_text="(UNUSED?) The type of object this is on maps",
    )
    latitude = models.DecimalField(
        max_digits=11, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=6, blank=True, null=True
    )
    zoom = models.SmallIntegerField(blank=True, null=True)
    shape = models.TextField(
        blank=True,
        null=False,
        help_text="Lat/long coordinate pairs, separated by semicolons, "
        "eg '51.513558,-0.104268;51.513552,-0.104518;...', "
        "from http://www.birdtheme.org/useful/v3largemap.html "
        "(formatted slightly differently).",
    )

    categories = models.ManyToManyField("Category", related_name="topics")

    diary_references = models.ManyToManyField("diary.Entry", related_name="topics")
    letter_references = models.ManyToManyField("letters.Letter", related_name="topics")

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    comment_name = "annotation"

    # Keeps track of whether we've made the order_title for this model yet.
    _order_title_made = False
    _original_categories_pks = []

    objects = TopicManager()

    class Meta:
        ordering = ["order_title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.summary_html = markdown(self.summary)
        self.wheatley_html = markdown(self.wheatley)
        super(Topic, self).save(*args, **kwargs)

        if self._order_title_made is False:
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
        if self.shape == "":
            return False
        else:
            points = self.shape.split(";")
            if points[0] == points[-1]:
                return True
            else:
                return False

    @property
    def has_path(self):
        """Do we have shape data, and does it describe a path (eg, a road)?"""
        if self.shape == "":
            return False
        else:
            points = self.shape.split(";")
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
                self.title, is_person=True
            )
        else:
            self.order_title = Topic.objects.make_order_title(
                self.title, is_person=False
            )

    def get_absolute_url(self):
        return reverse("topic_detail", kwargs={"pk": self.pk})

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return (
            (self.title, "A"),
            (self.summary, "B"),
            (self.wheatley, "B"),
            (self.wikipedia_html, "C"),
        )

    def get_annotated_diary_references(self):
        """
        Returns a list of lists, of this Topic's diary entry references.
        Doesn't include years/months where there are no referring Entries.
        [
            ['1660', [
                ['Jan', [Entry, Entry, Entry, ]],
                ['Mar', [Entry, Entry, ]],
            ]],
            ['1663', [
                ['Dec', [Entry, ]],
            ],
            ...
        ]
        """
        refs = []
        year_refs = []
        month_refs = []
        prev_year = None
        prev_yearmonth = None
        for ref in self.diary_references.order_by("diary_date"):
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
            return "https://en.wikipedia.org/wiki/{}".format(self.wikipedia_fragment)
        else:
            return ""

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
    enable_field = "allow_comments"


moderator.register(Topic, TopicModerator)
