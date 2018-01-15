#! -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.dates import _date_from_string,\
            ArchiveIndexView, DateDetailView, MonthArchiveView, YearArchiveView

from pepysdiary.common.views import BaseRSSFeed
from pepysdiary.diary.models import Entry, Summary


class EntryMixin(object):
    """
    All Entry-based views should probably inherit this.
    """
    model = Entry
    date_field = 'diary_date'
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'


class EntryDetailView(EntryMixin, DateDetailView):
    """
    Display a single entry based on the year/month/day in the URL.
    Assumes there is only one entry per date.
    """

    def get_object(self, queryset=None):
        """
        Get the object this request displays.
        This is mainly just overriding DateDetailView's get_object() method
        with the change that we don't call DetailView's get_object() method
        at the end, because we don't need a slug or pk.
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

        # Use a custom queryset if provided
        qs = queryset or self.get_queryset()

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(_("Future %(verbose_name_plural)s not available because %(class_name)s.allow_future is False.") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
            })

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        # date_field = self.get_date_field()
        # field = qs.model._meta.get_field(date_field)
        # lookup = _date_lookup_for_field(field, date)
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = qs.filter(**lookup_kwargs)

        # Here's where we differ from DateDetailView.get_object().
        # Instead of calling DetailView.get_object(), we just fetch an object
        # based on the date we've got.
        try:
            obj = qs.get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                              {'verbose_name': qs.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        context = super(EntryDetailView, self).get_context_data(**kwargs)
        context['tooltip_references'] = Entry.objects.get_brief_references(
                                                        objects=[self.object])
        extra_context = self.get_next_previous()
        context.update(extra_context)
        return context

    def get_next_previous(self):
        """
        Get the next/previous Entries based on the current Entry's date.
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()

        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

        try:
            previous_entry = self.model.objects.filter(
                        diary_date__lt=date).order_by('-diary_date')[:1].get()
        except self.model.DoesNotExist:
            previous_entry = None

        try:
            next_entry = self.model.objects.filter(
                        diary_date__gt=date).order_by('diary_date')[:1].get()
        except self.model.DoesNotExist:
            next_entry = None

        return {
            'previous_entry': previous_entry,
            'next_entry': next_entry,
        }


class EntryMonthArchiveView(EntryMixin, MonthArchiveView):
    """Show all the Entries from one month."""

    ordering = 'diary_date'

    def get_context_data(self, **kwargs):
        context = super(EntryMonthArchiveView, self).get_context_data(**kwargs)
        context['tooltip_references'] = Entry.objects.get_brief_references(
                                                objects=kwargs['object_list'])
        return context

    def get_ordering(self):
        return self.ordering


class EntryArchiveView(EntryMixin, ArchiveIndexView):
    """Show all the years and months there are Entries for."""

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.

        A copy of that in BaseArchiveIndexView, with the only change being
        that we're asking for 'month' rather than 'year' with get_date_list().
        """
        qs = self.get_dated_queryset()
        date_list = self.get_date_list(qs, 'month')

        if date_list:
            object_list = qs.order_by('-' + self.get_date_field())
        else:
            object_list = qs.none()

        return (date_list, object_list, {})


class SummaryYearArchiveView(YearArchiveView):
    """Show all the Summaries from one year."""
    model = Summary
    date_field = 'summary_date'
    make_object_list = True


class LatestEntriesFeed(BaseRSSFeed):
    title = "The Diary of Samuel Pepys"
    description = 'Daily entries from the 17th century London diary'

    def items(self):
        return Entry.objects.filter(
                diary_date__lte=Entry.objects.most_recent_entry_date()
            ).order_by('-diary_date')[:5]

    def item_description(self, item):
        return self.make_item_description(item.text)

    def item_author_name(self, item):
        return 'Samuel Pepys'

    def item_content_encoded(self, item):
        footnotes = ''
        if item.footnotes:
            footnotes = '<p><strong>Footnotes</strong></p>%s' % item.footnotes
        return self.make_item_content_encoded(
            text1=item.text,
            text2=footnotes,
            url=item.get_absolute_url(),
            comment_name=item.comment_name
        )
