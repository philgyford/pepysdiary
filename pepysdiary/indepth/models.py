from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils import timezone

from django_comments.moderation import CommentModerator, moderator
from markdown import markdown

from ..common.models import PepysModel
from .managers import PublishedArticleManager


class Article(PepysModel):
    """
    An In-Depth Article.
    """

    class Status(models.IntegerChoices):
        DRAFT = 10, "Draft"
        PUBLISHED = 20, "Published"

    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT,
        related_name="indepth_articles",
        help_text="Optional.",
    )
    intro = models.TextField(blank=False, null=False, help_text="Can use Markdown.")
    intro_html = models.TextField(
        blank=True,
        null=False,
        help_text="The intro field, with Markdown etc, turned into HTML.",
    )
    text = models.TextField(
        blank=True,
        null=False,
        help_text="Can use Markdown. Any images should be put in "
        "`pepysdiary/indepth/static/img/indepth/`.",
    )
    text_html = models.TextField(
        blank=True,
        null=False,
        help_text="The text field, with Markdown etc, turned into HTML.",
    )
    excerpt = models.TextField(blank=True, null=False)
    date_published = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(
        max_length=50, blank=False, null=False, unique_for_date="date_published"
    )
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    status = models.IntegerField(
        blank=False, null=False, choices=Status.choices, default=Status.DRAFT
    )

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    objects = models.Manager()
    published_articles = PublishedArticleManager()

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
            "article_detail",
            kwargs={
                "year": self.date_published.strftime("%Y"),
                "month": self.date_published.strftime("%m"),
                "day": self.date_published.strftime("%d"),
                "slug": self.slug,
            },
        )

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return ((self.title, "A"), (self.intro, "B"), (self.text, "B"))


class ArticleModerator(CommentModerator):
    email_notification = False
    enable_field = "allow_comments"


moderator.register(Article, ArticleModerator)
