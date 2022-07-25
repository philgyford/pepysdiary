import re

from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase, override_settings
from freezegun import freeze_time

from pepysdiary.common.utilities import make_datetime
from pepysdiary.membership.factories import PersonFactory
from pepysdiary.membership.managers import PersonManager
from pepysdiary.membership.models import Person


@freeze_time("2021-01-01 12:00:00", tz_offset=0)
class PersonManagerTestCase(TestCase):
    def _get_site_object(self):
        "For tests that require the Site object to have specific settings"
        site = Site.objects.first()
        site.domain = "example.com"
        site.name = "Pepys' Diary"
        site.save()
        return site

    def test_person_manager(self):
        "Ensure Person.objects, that we're using in tests, is a PersonManager"
        self.assertIsInstance(Person.objects, PersonManager)

    def test_create_user(self):
        "create_user() should correctly create a Person"
        Person.objects.create_user(
            name="Bob", email="bob@example.org", password="secret-password-here"
        )

        person = Person.objects.first()

        self.assertEqual(person.name, "Bob")
        self.assertEqual(person.email, "bob@example.org")
        self.assertTrue(person.is_active)
        self.assertFalse(person.is_staff)
        self.assertFalse(person.is_superuser)
        self.assertFalse(person.is_trusted_commenter)
        self.assertEqual(person.last_login, make_datetime("2021-01-01 12:00:00"))

    def test_create_user_returns_a_person(self):
        person = Person.objects.create_user(
            name="Bob", email="bob@example.org", password="secret-password-here"
        )
        self.assertIsInstance(person, Person)

    def test_create_user_email_required(self):
        "create_user() should require an email"
        with self.assertRaises(ValueError):
            Person.objects.create_user(name="Bob", password="secret-password-here")

    def test_create_user_name_required(self):
        "create_user() should require a name"
        with self.assertRaises(ValueError):
            Person.objects.create_user(
                email="bob@example.org", password="secret-password-here"
            )

    def test_create_superuser(self):
        "It should create a superuser"
        Person.objects.create_superuser(
            name="Bob", email="bob@example.org", password="secret-password-here"
        )

        person = Person.objects.first()

        self.assertEqual(person.name, "Bob")
        self.assertEqual(person.email, "bob@example.org")
        self.assertTrue(person.is_active)
        self.assertTrue(person.is_staff)
        self.assertTrue(person.is_superuser)
        self.assertFalse(person.is_trusted_commenter)
        self.assertEqual(person.last_login, make_datetime("2021-01-01 12:00:00"))

    def test_create_inactive_user(self):
        "It should create an inactive user"
        site = self._get_site_object()
        Person.objects.create_inactive_user(
            name="Bob",
            email="bob@example.org",
            password="secret-password-here",
            site=site,
        )

        person = Person.objects.first()

        self.assertEqual(person.name, "Bob")
        self.assertEqual(person.email, "bob@example.org")
        self.assertFalse(person.is_active)
        self.assertFalse(person.is_staff)
        self.assertFalse(person.is_superuser)
        self.assertFalse(person.is_trusted_commenter)
        self.assertEqual(person.last_login, make_datetime("2021-01-01 12:00:00"))

    def test_create_inactive_user_sets_activation_key(self):
        "Creating inactive user should set activation key to something that looks right"
        site = self._get_site_object()
        Person.objects.create_inactive_user(
            name="Bob",
            email="bob@example.org",
            password="secret-password-here",
            site=site,
        )

        person = Person.objects.first()

        self.assertTrue(re.search(r"^[a-f0-9]{40}$", person.activation_key))

    def test_create_inactive_user_sends_email(self):
        "The method should result in an activation email being sent"
        site = self._get_site_object()
        person = Person.objects.create_inactive_user(
            name="Bob",
            email="bob@example.org",
            password="secret-password-here",
            site=site,
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Activate your Pepys' Diary account")
        self.assertIn(
            f"https://example.com/account/activate/{person.activation_key}/",
            mail.outbox[0].body,
        )

    def test_create_inactive_user_send_email_false(self):
        "It shouldn't send email if send_email is false"
        site = self._get_site_object()
        Person.objects.create_inactive_user(
            name="Bob",
            email="bob@example.org",
            password="secret-password-here",
            site=site,
            send_email=False,
        )

        self.assertEqual(len(mail.outbox), 0)

    @override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    @freeze_time("2021-01-02 12:00:00", tz_offset=0)
    def test_activate_user_success(self):
        activation_key = "1234567890123456789012345678901234567890"
        person = PersonFactory(activation_key=activation_key, is_active=False)
        person.date_created = make_datetime("2021-01-01 12:00:01")
        person.save()

        person = Person.objects.activate_user(activation_key=activation_key)

        # Test the returned Person object.
        self.assertEqual(person.date_activated, make_datetime("2021-01-02 12:00:00"))
        self.assertEqual(person.activation_key, "ALREADY_ACTIVATED")
        self.assertTrue(person.is_active)

        # Test the data was saved to the database:
        person_from_db = Person.objects.first()
        self.assertEqual(
            person_from_db.date_activated, make_datetime("2021-01-02 12:00:00")
        )
        self.assertEqual(person_from_db.activation_key, "ALREADY_ACTIVATED")
        self.assertTrue(person_from_db.is_active)

    @override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    @freeze_time("2021-01-02 12:00:00", tz_offset=0)
    def test_activate_user_invalid_activation_key_format(self):
        "If the activation key is not of the right format, it should return false."
        # There's a matching user, so it should otherwise work, but we want to check
        # that we validate the format of the key before querying the database:
        person = PersonFactory(activation_key="1234567890", is_active=False)
        person.date_created = make_datetime("2021-01-01 12:00:01")
        person.save()

        person = Person.objects.activate_user(activation_key="1234567890")

        self.assertFalse(person)
        # Double check the person in the database hasn't been updated:
        person_from_db = Person.objects.first()
        self.assertIsNone(person_from_db.date_activated)
        self.assertEqual(person_from_db.activation_key, "1234567890")
        self.assertFalse(person_from_db.is_active)

    @override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    @freeze_time("2021-01-02 12:00:00", tz_offset=0)
    def test_activate_user_non_matching_activation_key(self):
        "If activation key is the correct format, but there's no matching user, False"
        person = PersonFactory(
            activation_key="abcdefghijabcdefghijabcdefghijabcdefghij", is_active=False
        )
        person.date_created = make_datetime("2021-01-01 12:00:01")
        person.save()

        person = Person.objects.activate_user(
            activation_key="1234567890123456789012345678901234567890"
        )

        self.assertFalse(person)
        # Double check the person in the database hasn't been updated:
        person_from_db = Person.objects.first()
        self.assertIsNone(person_from_db.date_activated)
        self.assertEqual(
            person_from_db.activation_key, "abcdefghijabcdefghijabcdefghijabcdefghij"
        )
        self.assertFalse(person_from_db.is_active)

    @override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    @freeze_time("2021-01-02 12:00:00", tz_offset=0)
    def test_activate_user_activation_key_expired(self):
        "If everything else is fine, but the key has expired, it should return False"
        activation_key = "1234567890123456789012345678901234567890"
        person = PersonFactory(activation_key=activation_key, is_active=False)
        # Too late:
        person.date_created = make_datetime("2021-01-01 12:00:00")
        person.save()

        person = Person.objects.activate_user(activation_key=activation_key)

        self.assertFalse(person)
        # Double check the person in the database hasn't been updated:
        person_from_db = Person.objects.first()
        self.assertIsNone(person_from_db.date_activated)
        self.assertEqual(person_from_db.activation_key, activation_key)
        self.assertFalse(person_from_db.is_active)
