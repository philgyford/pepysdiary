import factory

from pepysdiary.common.utilities import make_date
from pepysdiary.events.models import DayEvent


class DayEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DayEvent

    title = factory.Faker("sentence", nb_words=2)
    event_date = factory.Faker(
        "date_between_dates",
        date_start=make_date("1660-01-01"),
        date_end=make_date("1669-05-31"),
    )
    source = DayEvent.Source.GADBURY
