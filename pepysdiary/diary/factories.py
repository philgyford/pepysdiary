import factory

from pepysdiary.diary.models import Entry, Summary
from pepysdiary.common.utilities import make_date


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entry

    title = factory.LazyAttribute(lambda o: o.diary_date.strftime("%A %-d %B %Y"))
    diary_date = factory.Faker(
        "date_between_dates",
        date_start=make_date("1660-01-01"),
        date_end=make_date("1669-05-31"),
    )
    text = "<p>A test diary entry.</p>"


class SummaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Summary

    title = factory.LazyAttribute(lambda o: o.summary_date.strftime("%B %Y"))
    summary_date = factory.Faker(
        "date_between_dates",
        date_start=make_date("1660-01-01"),
        date_end=make_date("1669-05-01"),
    )
    text = "A test diary summary."
