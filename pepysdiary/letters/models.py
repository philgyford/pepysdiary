import re

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django_comments.moderation import CommentModerator, moderator

from pepysdiary.common.models import OldDateMixin, PepysModel
from pepysdiary.encyclopedia.models import Topic

from .managers import LetterManager


class Letter(PepysModel, OldDateMixin):
    class Source(models.IntegerChoices):
        GUY_DE_LA_BEDOYERE = 10, "Guy de la Bédoyère - Particular Friends"
        GUY_DE_LA_BEDOYERE_2 = 15, "Guy de la Bédoyère - The Letters of Samuel Pepys"
        HELEN_TRUESDELL_HEATH = (
            20,
            "Helen Truesdell Heath - The Letters of Samuel Pepys and his Family Circle",
        )
        KEITH_PHELPS = 30, "Keith Phelps"

    title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        help_text='eg, "Thomas Hill to Samuel Pepys".',
    )
    letter_date = models.DateField(blank=False, null=False)
    display_date = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        help_text='eg "Thursday 27 April 1665". Because days of the week '
        "are calculated wrong for old dates.",
    )
    text = models.TextField(blank=False, null=False, help_text="Should be HTML.")
    footnotes = models.TextField(blank=True, null=False, help_text="Should be HTML.")
    excerpt = models.TextField(
        blank=False,
        null=False,
        help_text="200 or so characters from the start of the letter, after "
        "salutations.",
    )
    sender = models.ForeignKey(
        "encyclopedia.Topic",
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="letters_sent",
    )
    recipient = models.ForeignKey(
        "encyclopedia.Topic",
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="letters_received",
    )
    source = models.IntegerField(blank=True, null=True, choices=Source.choices)
    slug = models.SlugField(
        max_length=50, blank=False, null=False, unique_for_date="letter_date"
    )
    comment_count = models.IntegerField(default=0, blank=False, null=False)
    last_comment_time = models.DateTimeField(blank=True, null=True)
    allow_comments = models.BooleanField(blank=False, null=False, default=True)
    order = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        default=0,
        help_text="If letters are from the same day, this is used to order them, "
        "lowest number first.",
    )

    old_date_field = "letter_date"
    comment_name = "annotation"

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    # Will also have a 'topics' ManyToMany field, from Topic.

    objects = LetterManager()

    class Meta:
        ordering = [
            "letter_date",
            "order",
        ]
        indexes = [GinIndex(fields=["search_document"])]

    def __str__(self):
        return f"{self.letter_date}: {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.make_references()

    def get_absolute_url(self):
        return reverse(
            "letter_detail",
            kwargs={
                "year": self.year,
                "month": self.month,
                "day": self.day,
                "slug": self.slug,
            },
        )

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return (
            (self.title, "A"),
            (self.text, "B"),
            (self.footnotes, "C"),
        )

    def make_references(self):
        """
        Sets all the Encyclopedia Topics the text of this letter (and
        footnotes) refers to. Saves them to the database.
        """
        self.topics.clear()
        # Get a list of all the Topic IDs mentioned in text and footnotes:
        ids = re.findall(
            r"pepysdiary.com\/encyclopedia\/(\d+)\/", f"{self.text} {self.footnotes}"
        )
        # Make sure list of Topic IDs is unique:
        # From http://stackoverflow.com/a/480227/250962
        seen = set()
        seen_add = seen.add
        unique_ids = [id for id in ids if id not in seen and not seen_add(id)]

        for id in unique_ids:
            topic = Topic.objects.get(pk=id)
            topic.letter_references.add(self)

    @property
    def short_date(self):
        """
        Shorter than self.display_date, like '27 Apr 1665'.
        """
        return f"{self.day_e} {self.month_b} {self.year}"

    @property
    def full_title(self):
        """
        Uniquish title including correspondents and date, like
        '27 April 1665, Samuel Pepys to John Evelyn'.
        """
        return f"{self.short_date}, {self.title}"


class LetterModerator(CommentModerator):
    email_notification = False
    enable_field = "allow_comments"


moderator.register(Letter, LetterModerator)
