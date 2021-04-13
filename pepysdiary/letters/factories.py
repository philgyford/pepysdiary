import factory

from pepysdiary.common.utilities import make_date
from pepysdiary.letters.models import Letter


class LetterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Letter

    title = factory.Faker("text", max_nb_chars=100)
    letter_date = factory.Faker(
        "date_between_dates",
        date_start=make_date("1665-04-27"),
        date_end=make_date("1673-04-14"),
    )
    # Will be nonsense but needs to be something:
    display_date = factory.Faker("text", max_nb_chars=50)
    text = factory.Faker("paragraph")
    excerpt = factory.Faker("text", max_nb_chars=200)
    sender = factory.SubFactory("pepysdiary.encyclopedia.factories.PersonTopicFactory")
    recipient = factory.SubFactory(
        "pepysdiary.encyclopedia.factories.PersonTopicFactory"
    )
    slug = factory.Sequence(lambda n: "letter%d" % n)
