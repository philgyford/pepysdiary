from django.urls import reverse
from django.db import models
from django.utils import timezone

from django_comments.moderation import CommentModerator, moderator
from markdown import markdown

from pepysdiary.common.models import PepysModel


class PublishedArticleManager(models.Manager):
    """
    All Articles that have been Published.
    """
    def get_queryset(self):
        return super(PublishedArticleManager, self).get_queryset().filter(
                                               status=Article.STATUS_PUBLISHED)


class Article(PepysModel):
    """
    An In-Depth Article.
    """

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
        help_text="Can use Markdown. Any images should be put in `pepysdiary/indepth/static/img/indepth/`.")
    text_html = models.TextField(blank=True, null=False,
            help_text="The text field, with Markdown etc, turned into HTML.")
    excerpt = models.TextField(blank=True, null=False)
    date_published = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(max_length=50, blank=False, null=False,
                                            unique_for_date='date_published')
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)

    status = models.IntegerField(blank=False, null=False,
                                choices=STATUS_CHOICES, default=STATUS_DRAFT)

    objects = models.Manager()
    published_articles = PublishedArticleManager()

    class Meta:
        ordering = ['-date_published', ]

    def __str__(self):
        return '%s' % (self.title)

    def save(self, *args, **kwargs):
        self.intro_html = markdown(self.intro)
        self.text_html = markdown(self.text)
        if self.date_published is None and self.status == self.STATUS_PUBLISHED:
            # If we're published, and the date_published hasn't been set,
            # then set it.
            self.date_published = timezone.now()

        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={
                'year': self.date_published.strftime('%Y'),
                'month': self.date_published.strftime('%m'),
                'day': self.date_published.strftime('%d'),
                'slug': self.slug,
            })


class ArticleModerator(CommentModerator):
    email_notification = False
    enable_field = 'allow_comments'

moderator.register(Article, ArticleModerator)
