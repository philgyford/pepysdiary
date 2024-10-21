from itertools import chain

from django.conf import settings
from django.db.models import Count, F, Q
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Topic.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["person"] = self.object
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
        return queryset

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

        I can't believe what a convoluted way I've ended up doing this.
        There must be an easier way.
        """
        # Get both senders and recipients' topic_ids, with counts of how many letters:
        senders = (
            Letter.objects.order_by()
            .values(topic_id=F("sender"))
            .annotate(count=Count("pk"))
            .distinct()
        )
        recipients = (
            Letter.objects.order_by()
            .values(topic_id=F("recipient"))
            .annotate(count=Count("pk"))
            .distinct()
        )
        senders_and_recipients = list(chain(senders, recipients))

        # Combine above into topic_id: totalcount of letters:
        topic_id_to_count = {}
        for row in senders_and_recipients:
            if row["topic_id"] in topic_id_to_count:
                topic_id_to_count[row["topic_id"]] += row["count"]
            else:
                topic_id_to_count[row["topic_id"]] = row["count"]

        topics = Topic.objects.filter(id__in=topic_id_to_count.keys())
        for topic in topics:
            topic.letter_count = topic_id_to_count[topic.id]

        return sorted(list(topics), key=lambda t: t.letter_count, reverse=True)


class LetterFromPersonView(LetterPersonView):
    letter_kind = "from"

    def get_queryset(self):
        return Letter.objects.filter(sender=self.object)


class LetterToPersonView(LetterPersonView):
    letter_kind = "to"

    def get_queryset(self):
        return Letter.objects.filter(recipient=self.object)


class LetterArchiveView(RedirectView):
    permanent = False
    query_string = False
    pattern_name = "letter_person"

    def get_redirect_url(self, *args, **kwargs):
        "Redirect from front /letters/ page to the page for Pepys's letters"
        return reverse(self.pattern_name, kwargs={"pk": settings.PEPYS_TOPIC_ID})
