import datetime
import re

import hashlib
from django.contrib.auth.models import BaseUserManager
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import smart_str
import pytz


SHA1_RE = re.compile(r"^[a-f0-9]{40}$")


class PersonManager(BaseUserManager):
    """
    Many of the activation-related methods are taken from
    django-registration.
    """

    def create_user(self, name=None, email=None, password=None, **extra_fields):
        """
        Creates and saves a Person with the given name, email and password.
        """
        now = timezone.now()

        if not email:
            raise ValueError("Users must have an email address")

        if not name:
            raise ValueError("Users must have a name")

        email = PersonManager.normalize_email(email)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(name=name, email=email, last_login=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, **extra_fields):
        u = self.create_user(name, email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

    def create_inactive_user(
        self, name, email, password, site, send_email=True, **extra_fields
    ):
        """
        Create a new, inactive ``User`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.
        """
        from .models import Person

        with transaction.atomic():
            person = Person.objects.create_user(name, email, password, **extra_fields)
            person.is_active = False
            person.save()

            person = self._set_activation_key(person)

            if send_email:
                person.send_activation_email(site)

            return person

    def _set_activation_key(self, person):
        username = smart_str(person.name)
        hash_input = (get_random_string(5) + username).encode("utf-8")
        person.activation_key = hashlib.sha1(hash_input).hexdigest()
        person.save()
        return person

    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.

        If the key is valid and has not expired, return the ``User``
        after activating.

        If the key is not valid or has expired, return ``False``.

        If the key is valid but the ``User`` is already active,
        return ``False``.

        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``Person.ACTIVATED``
        after successful activation.

        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key.lower()):
            try:
                person = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if person.activation_key_expired() is False:
                person.is_active = True
                person.date_activated = datetime.datetime.now(pytz.utc)
                person.activation_key = self.model.ACTIVATED
                person.save()
                return person
        return False
