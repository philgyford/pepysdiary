from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.dates import DateDetailView
from django.views.generic.list import ListView

from pepysdiary.common.views import BaseRSSFeed
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.letters.models import Letter


class LetterDetailView(DateDetailView):
    model = Letter
    date_field = 'letter_date'
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'

    def get_context_data(self, **kwargs):
        context = super(LetterDetailView, self).get_context_data(**kwargs)
        context['tooltip_references'] = Letter.objects.get_brief_references(
                                                        objects=[self.object])
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
            previous_letter = self.model.objects \
                                .filter( \
                                    Q(letter_date__lte=date, order__lt=order) \
                                    | \
                                    Q(letter_date__lt=date) \
                                ) \
                                .order_by('-letter_date', '-order')[:1] \
                                .get()
        except self.model.DoesNotExist:
            previous_letter = None

        try:
            next_letter = self.model.objects \
                                .filter( \
                                    Q(letter_date__gte=date, order__gt=order) \
                                    | \
                                    Q(letter_date__gt=date) \
                                ) \
                                .order_by('letter_date', 'order')[:1] \
                                .get()
        except self.model.DoesNotExist:
            next_letter = None

        return {
            'previous_letter': previous_letter,
            'next_letter': next_letter,
        }


class LetterPersonView(ListView):
    """
    For displaying all the Letters sent from/to an individual.
    Just needs the pk of a Topic in the People Category.
    """
    model = Letter
    template_name = 'letter_person.html'
    allow_empty = False
    # Will be populated with a Topic in get_queryset().
    person = None

    def get(self, request, *args, **kwargs):
        """
        If we're linking to a page with SP's ID, then redirect to the general
        Letters page.
        """
        if int(kwargs.get('pk', 0)) == settings.PEPYS_TOPIC_ID:
            return redirect('letters')
        return super(LetterPersonView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        try:
            topic = Topic.objects.get(pk=self.kwargs['pk'])
        except Topic.DoesNotExist:
            raise Http404(
                    "Topic matching pk '%s' does not exist." % self.kwargs.pk)

        # We did check that the topic was in the People Category, but we don't
        # need to, as we show a 404 if there's nothing found anyway.

        self.person = topic

        queryset = self.model.objects.filter(
                                        Q(sender=topic) | Q(recipient=topic))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LetterPersonView, self).get_context_data(**kwargs)
        context['person'] = self.person
        return context


class LetterArchiveView(TemplateView):
    template_name = 'letter_list.html'

    def get_context_data(self, **kwargs):
        context = super(LetterArchiveView, self).get_context_data(**kwargs)
        context['letters'] = Letter.objects.all()
        return context


class LatestLettersFeed(BaseRSSFeed):
    title = "Pepys' Diary - Letters"
    description = "Letters sent by or to Samuel Pepys"

    def items(self):
        return Letter.objects.all().order_by('-date_created')[:3]

    def item_pubdate(self, item):
        return item.date_created

    def item_description(self, item):
        return self.make_item_description(item.text)

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            text1=item.text,
            text2=item.footnotes,
            url=item.get_absolute_url(),
            comment_name=item.comment_name
        )
