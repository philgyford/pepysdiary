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

            person = self.set_activation_key(person)

            if send_email:
                person.send_activation_email(site)

            return person

    def set_activation_key(self, person):
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
                person.save()
                person.activation_key = self.model.ACTIVATED
                person.save()
                return person
        return False

    def delete_expired_users(self):
        """
        Tweaked from django-registration.

        Remove expired People.

        Any ``Person`` who is both inactive and has an expired activation
        key will be deleted.

        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupactivation``.

        Regularly clearing out accounts which have never been
        activated serves two useful purposes:

        1. It alleviates the ocasional need to reset an
           activation key and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.

        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.

        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply set their
        activation_key to the value of Person.ACTIVATED and set their
        is_active to False. They will not be deleted but will be unable
        to log in.

        """
        for person in self.all():
            if person.activation_key_expired() is True:
                if not person.is_active:
                    person.delete()
