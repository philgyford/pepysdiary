import factory

from pepysdiary.membership.models import Person


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.Faker("name")
    email = factory.Faker("email")
    password = "password"


class StaffPersonFactory(PersonFactory):
    is_staff = True
