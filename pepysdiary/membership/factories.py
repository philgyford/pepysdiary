import factory

from pepysdiary.membership.models import Person


class PersonFactory(factory.django.DjangoModelFactory):
    """If passing in a password, best to do it like:

    from django.contrib.auth.hashers import make_password

    PersonFactory(password=make_password("my-password))
    """

    class Meta:
        model = Person

    name = factory.Faker("name")
    email = factory.Faker("email")
    password = "password"
    is_active = True
    activation_key = "ALREADY_ACTIVATED"


class StaffPersonFactory(PersonFactory):
    is_staff = True
    is_admin = False
