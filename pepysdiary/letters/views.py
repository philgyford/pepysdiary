from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
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
        context = super(LetterDetailView, self).get_context_data(**kwargs)
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
    allow_empty = False

    def get(self, request, *args, **kwargs):
        """
        If we're linking to a page with SP's ID, then redirect to the general
        Letters page.
        """
        if int(kwargs.get("pk", 0)) == settings.PEPYS_TOPIC_ID:
            return redirect("letters")

        self.object = self.get_object(queryset=Topic.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["person"] = self.object
        context["letter_list"] = context["object_list"]
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


class LetterArchiveView(TemplateView):
    template_name = "letters/letter_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["letters"] = Letter.objects.all()
        return context
