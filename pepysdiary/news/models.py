from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from markdown import markdown

from pepysdiary.common.models import PepysModel


class PublishedPostManager(models.Manager):
    """
    All Posts that have been Published.
    """
    def get_query_set(self):
        return super(PublishedPostManager, self).get_query_set().filter(
                                               status=Post.STATUS_PUBLISHED)

    def is_valid_category_slug(self, slug):
        """
        Is `slug` a valid Post category?
        """
        valid_slugs = [k for k, v in Post.CATEGORY_CHOICES]
        if slug in valid_slugs:
            return True
        else:
            return False

    def category_slug_to_name(self, slug):
        """
        Assuming slug is a valid category slug, return the name.
        Else, ''.
        """
        name = ''
        for k, v in Post.CATEGORY_CHOICES:
            if k == slug:
                name = v
        return name


class Post(PepysModel):
    """
    A Site News Post.
    """

    # These are used as slugs in URLs.
    CATEGORY_EVENTS = 'events'
    CATEGORY_HOUSEKEEPING = 'housekeeping'
    CATEGORY_FEATURES = 'new-features'
    CATEGORY_MEDIA = 'pepys-in-the-media'
    CATEGORY_PRESS = 'press'
    CATEGORY_STATISTICS = 'statistics'
    CATEGORY_CHOICES = (
        (CATEGORY_EVENTS, 'Events'),
        (CATEGORY_HOUSEKEEPING, 'Housekeeping'),
        (CATEGORY_FEATURES, 'New features'),
        (CATEGORY_MEDIA, 'Pepys in the media'),
        (CATEGORY_PRESS, 'Press for this site'),
        (CATEGORY_STATISTICS, 'Site statistics'),
    )

    STATUS_DRAFT = 10
    STATUS_PUBLISHED = 20
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    )

    title = models.CharField(max_length=255, blank=False, null=False)
    intro = models.TextField(blank=False, null=False,
                                                help_text="Can use Markdown.")
    intro_html = models.TextField(blank=True, null=False,
            help_text="The intro field, with Markdown etc, turned into HTML.")
    text = models.TextField(blank=True, null=False,
        help_text="Can use Markdown. Images go in `pepysdiary/news/static/img/news/`. Files go in `pepysdiary/news/static/files/news/`")
    text_html = models.TextField(blank=True, null=False,
            help_text="The text field, with Markdown etc, turned into HTML.")
    date_published = models.DateTimeField(blank=True, null=True)
    comment_count = models.IntegerField(default=0, blank=False, null=False)

    status = models.IntegerField(blank=False, null=False,
                                choices=STATUS_CHOICES, default=STATUS_DRAFT)
    category = models.CharField(max_length=25, blank=False, null=False,
                                    db_index=True, choices=CATEGORY_CHOICES)

    objects = models.Manager()
    published_posts = PublishedPostManager()

    class Meta:
        ordering = ['-date_published', ]

    def __unicode__(self):
        return u'%s' % (self.title)

    def save(self, *args, **kwargs):
        self.intro_html = markdown(self.intro)
        self.text_html = markdown(self.text)
        if self.date_published is None and \
                                        self.status == self.STATUS_PUBLISHED:
            # If we're published, and the date_published hasn't been set,
            # then set it.
            self.date_published = timezone.now()

        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={
                'year': self.date_published.strftime('%Y'),
                'month': self.date_published.strftime('%m'),
                'day': self.date_published.strftime('%d'),
                'pk': self.pk,
            })
