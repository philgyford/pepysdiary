from django.conf import settings
from django.db.models import Count, Q
from django.urls import reverse
from django.views.generic.base import RedirectView
from django.views.generic.dates import DateDetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView

from pepysdiary.encyclopedia.models import Topic

from .models import Letter


class LetterDetailView(DateDetailView):
    model = Letter
    date_field = "letter_date"
    year_format = "%Y"
    month_format = "%m"
    day_format = "%d"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tooltip_references"] = Letter.objects.get_brief_references(
            objects=[self.object]
        )
        extra_context = self.get_next_previous()
        context.update(extra_context)
        return context

    def get_next_previous(self):
        """
        Get the next/previous Letters based on the current Letter's date.
        """
        date = self.object.letter_date
        order = self.object.order

        try:
            previous_letter = (
                self.model.objects.filter(
                    Q(letter_date__lte=date, order__lt=order) | Q(letter_date__lt=date)
                )
                .order_by("-letter_date", "-order")[:1]
                .get()
            )
        except self.model.DoesNotExist:
            previous_letter = None

        try:
            next_letter = (
                self.model.objects.filter(
                    Q(letter_date__gte=date, order__gt=order) | Q(letter_date__gt=date)
                )
                .order_by("letter_date", "order")[:1]
                .get()
            )
        except self.model.DoesNotExist:
            next_letter = None

        return {
            "previous_letter": previous_letter,
            "next_letter": next_letter,
        }


class LetterPersonView(SingleObjectMixin, ListView):
    """
    For displaying all the Letters sent from/to an individual.
    Just needs the pk of a Topic in the People Category.
    """

    template_name = "letters/letter_person.html"
    allow_empty = True

    # In child classes this will be "from" or "to".
    # Indicates the sort of list of letters to/from this person (or both)
    letter_kind = "both"

    ordering = "letter_date"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Topic.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["person"] = self.object
        context["ordering"] = self.ordering
        context["letter_list"] = context["object_list"]
        context["letter_kind"] = self.letter_kind
        context["letter_counts"] = self.get_letter_counts()
        context["correspondents"] = self.get_correspondents()
        return context

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        queryset = Letter.objects.filter(
            Q(sender=self.object) | Q(recipient=self.object)
        )
        queryset = queryset.order_by(self.get_ordering())
        return queryset

    def get_ordering(self):
        if self.request.GET.get("o", "") == "added":
            self.ordering = "-date_created"
        return super().get_ordering()

    def get_letter_counts(self):
        return {
            "from": Letter.objects.filter(sender=self.object).count(),
            "to": Letter.objects.filter(recipient=self.object).count(),
            "both": Letter.objects.filter(
                Q(sender=self.object) | Q(recipient=self.object)
            ).count(),
        }

    def get_correspondents(self):
        """
        Returns a list of Topics, each one a person with
        a letter_count attribute. Ordered by letter_count descending.

        Should be able to get all this in one query, but I get an
        error if I try to get the full Topic objects with the count annotation:

            column "encyclopedia_topic.date_created" must appear in the
            GROUP BY clause or be used in an aggregate function

        So we're getting the ids and counts,
        then getting the Topics for those ids,
        and then adding the counts to the Topics.
        """
        letter_counts = (
            Topic.objects.values("id")
            .annotate(
                letter_count=(
                    Count("letters_sent", distinct=True)
                    + Count("letters_received", distinct=True)
                )
            )
            .filter(letter_count__gt=0)
            .order_by("-letter_count")
        )

        # Put into dict:
        topic_id_to_count = {t["id"]: t["letter_count"] for t in letter_counts}

        # Get all the Topics and add their letter_count to each:
        topics = Topic.objects.filter(id__in=topic_id_to_count.keys())
        for topic in topics:
            topic.letter_count = topic_id_to_count[topic.id]

        return sorted(list(topics), key=lambda t: t.letter_count, reverse=True)


class LetterFromPersonView(LetterPersonView):
    letter_kind = "from"

    def get_queryset(self):
        queryset = Letter.objects.filter(sender=self.object)
        queryset = queryset.order_by(self.get_ordering())
        return queryset


class LetterToPersonView(LetterPersonView):
    letter_kind = "to"

    def get_queryset(self):
        queryset = Letter.objects.filter(recipient=self.object)
        queryset = queryset.order_by(self.get_ordering())
        return queryset


class LetterArchiveView(RedirectView):
    permanent = False
    query_string = False
    pattern_name = "letter_person"

    def get_redirect_url(self, *args, **kwargs):
        "Redirect from front /letters/ page to the page for Pepys's letters"
        return reverse(self.pattern_name, kwargs={"pk": settings.PEPYS_TOPIC_ID})
