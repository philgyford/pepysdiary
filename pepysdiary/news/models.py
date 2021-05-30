from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.urls import reverse
from django.utils import timezone

from django_comments.moderation import CommentModerator, moderator
from markdown import markdown

from .managers import PublishedPostManager
from ..common.models import PepysModel


class Post(PepysModel):
    """
    A Site News Post.
    """

    class Category(models.TextChoices):
        # These are used as slugs in URLs.
        EVENTS = "events", "Events"
        HOUSEKEEPING = "housekeeping", "Housekeeping"
        FEATURES = "new-features", "New features"
        MEDIA = "pepys-in-the-media", "Pepys in the media"
        PRESS = "press", "Press for this site"
        STATISTICS = "statistics", "Site statistics"

    class Status(models.IntegerChoices):
        DRAFT = 10, "Draft"
        PUBLISHED = 20, "Published"

    title = models.CharField(max_length=255, blank=False, null=False)
    intro = models.TextField(blank=False, null=False, help_text="Can use Markdown.")
    intro_html = models.TextField(
        blank=True,
        null=False,
        help_text="The intro field, with Markdown etc, turned into HTML.",
    )
    text = models.TextField(
        blank=True,
        null=False,
        help_text="Can use Markdown. Images go in "
        "`pepysdiary/news/static/img/news/`. Files go in "
        "`pepysdiary/news/static/files/news/`",
    )
    text_html = models.TextField(
        blank=True,
        null=False,
        help_text="The text field, with Markdown etc, turned into HTML.",
    )
    date_published = models.DateTimeField(blank=True, null=True)
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    status = models.IntegerField(
        blank=False, null=False, choices=Status.choices, default=Status.DRAFT
    )
    category = models.CharField(
        max_length=25, blank=False, null=False, db_index=True, choices=Category.choices
    )

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    objects = models.Manager()
    published_posts = PublishedPostManager()

    class Meta:
        ordering = ["-date_published"]

    def __str__(self):
        return "%s" % (self.title)

    def save(self, *args, **kwargs):
        self.intro_html = markdown(self.intro)
        self.text_html = markdown(self.text)
        if self.date_published is None and self.status == self.Status.PUBLISHED:
            # If we're published, and the date_published hasn't been set,
            # then set it.
            self.date_published = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "post_detail",
            kwargs={
                "year": self.date_published.strftime("%Y"),
                "month": self.date_published.strftime("%m"),
                "day": self.date_published.strftime("%d"),
                "pk": self.pk,
            },
        )

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return ((self.title, "A"), (self.intro, "B"), (self.text, "B"))

    @property
    def category_title(self):
        """
        Return the title of this Post's category.
        e.g. "New features".
        """
        categories = {c[0]: c[1] for c in self.Category.choices}
        return categories[self.category]

    @classmethod
    def is_valid_category_slug(self, slug):
        "Is `slug` a valid Post category?"
        return slug in Post.Category.values

    @classmethod
    def category_slug_to_name(self, slug):
        """
        Assuming slug is a valid category slug, return the name.
        Else, ''.
        """
        name = ""
        for k, v in Post.Category.choices:
            if k == slug:
                name = v
        return name


class PostModerator(CommentModerator):
    email_notification = False
    enable_field = "allow_comments"


moderator.register(Post, PostModerator)
