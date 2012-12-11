from django.db import models

from markdown import markdown

from pepysdiary.common.models import PepysModel


class TopicManager(models.Manager):
    def make_order_title(self, title):
        return title


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
    summary = models.TextField(blank=True, null=False)
    summary_html = models.TextField(blank=True, null=False,
        help_text="The summary field, with Markdown etc, turned into HTML")
    wheatley = models.TextField(blank=True, null=False,
        help_text="Taken from footnotes in the 1893 Wheatley edition of the diary")
    wheatley_html = models.TextField(blank=True, null=False,
        help_text="The wheatley field, with Markdown etc, turned into HTML")
    tooltip_text = models.TextField(blank=True, null=False,
                        help_text="For hovering over links in diary entries.")
    wikipedia_fragment = models.CharField(
        max_length=255, blank=True, null=False,
        help_text="From the Wikipedia page URL, if any, eg, 'Samuel_Pepys'.")
    thumbnail = models.ImageField(upload_to='encyclopedia/thumbnails',
        blank=True, null=True, help_text="100 x 120 pixels")
    comment_count = models.IntegerField(default=0, blank=False, null=False)

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

    objects = TopicManager()

    class Meta:
        ordering = ['title', ]

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.order_title = Topic.objects.make_order_title(self.title)
        self.summary_html = markdown(self.summary)
        self.wheatley_html = markdown(self.wheatley)
        super(Topic, self).save(*args, **kwargs)
