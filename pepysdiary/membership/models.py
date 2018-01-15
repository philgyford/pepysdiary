import datetime
import hashlib
import pytz
import random
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,\
                                                                BaseUserManager
from django.contrib.auth.signals import user_logged_in
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.utils import timezone

from pepysdiary.membership.utilities import email_user, validate_person_name


SHA1_RE = re.compile('^[a-f0-9]{40}$')


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
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')
        email = PersonManager.normalize_email(email)
        user = self.model(name=name, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, **extra_fields)

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

    def create_inactive_user(self, name, email, password, site,
                                            send_email=True, **extra_fields):
        """
        Create a new, inactive ``User`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.

        """
        with transaction.atomic():
            person = Person.objects.create_user(
                                            name, email, password, **extra_fields)
            person.is_active = False
            person.save()

            person = self.set_activation_key(person)

            if send_email:
                person.send_activation_email(site)

            return person

    def set_activation_key(self, person):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        name = person.name
        if isinstance(name, str):
            name = name.encode('utf-8')
        person.activation_key = hashlib.sha1(salt + name).hexdigest()
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
        if SHA1_RE.search(activation_key):
            try:
                person = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not person.activation_key_expired():
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
            if person.activation_key_expired():
                if not person.is_active:
                    person.delete()


class Person(AbstractBaseUser, PermissionsMixin):
    """
    Our custom User class.
    No usernames - just `email` and `password`. Plus a unique `name` which is
    what the user wants to be known as.

    I ran this to translate my one User to a Person:

        INSERT INTO membership_person(id, name, email, password, last_login, is_superuser, is_staff, is_active, date_created, date_modified) SELECT id, username, email, password, last_login, is_superuser, is_staff, is_active, date_joined, date_joined FROM auth_user;

    And to make the Django 1.4 comments and flags work with the new Person
    model I did this:

        ALTER TABLE django_comments DROP CONSTRAINT django_comments_user_id_fkey;
        ALTER TABLE django_comments ADD CONSTRAINT django_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES membership_person(id) DEFERRABLE INITIALLY DEFERRED;

        ALTER TABLE django_comment_flags DROP CONSTRAINT django_comment_flags_user_id_fkey;
        ALTER TABLE django_comment_flags ADD CONSTRAINT django_comment_flags_user_id_fkey FOREIGN KEY (user_id) REFERENCES membership_person(id) DEFERRABLE INITIALLY DEFERRED;

    Note: I didn't have any existing comments/flags that were related to old
    User objects. If I did, that might all not have worked.
    """
    # The value that `activation_key` will be set to after the user has
    # activated their account.
    ACTIVATED = 'ALREADY_ACTIVATED'

    # ALSO HAS:
    # password
    # last_login
    # is_superuser
    # user_permissions
    # groups

    email = models.EmailField(verbose_name='Email address', max_length=255,
                                                unique=True, db_index=True, )
    name = models.CharField(max_length=50, unique=True,
                        help_text="Publically visible name, spaces allowed",
                        validators=[validate_person_name])
    url = models.URLField(verbose_name='URL', max_length=255, blank=True,
                                                                    null=True)
    is_staff = models.BooleanField(verbose_name='Is staff?', default=False,
        help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(verbose_name='Is active?', default=False,
        help_text='Designates whether this user should be treated as '
                        'active. Unselect this instead of deleting accounts.')
    is_trusted_commenter = models.BooleanField(
            verbose_name='Is trusted commenter?', default=False,
            help_text="Allows them to post comments without spam-filtering")
    activation_key = models.CharField(max_length=40,
            help_text="Will be 'ALREADY_ACTIVATED' when 'Is active?' is true.")
    first_comment_date = models.DateTimeField(blank=True, null=True,
        help_text="First time they commented. Might be before the date they joined...")
    date_activated = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = PersonManager()

    class Meta:
        verbose_name_plural = 'People'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk, })

    def __unicode__(self):
        return self.name

    def activation_key_expired(self):
        """
        Determine whether this ``Person``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.

        Key expiration is determined by a two-step process:

        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.

        """
        expiration_date = datetime.timedelta(
                                        days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
           (self.date_created + expiration_date <= datetime.datetime.now(
                                                                    pytz.utc))
    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        """
        This largely taken from django-registration.

        Send a activation email to the user.

        The email template will receive the following context
        variables:

        ``activation_key``
            The activation key for the new account.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.models.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        """
        ctx_dict = {'activation_key': self.activation_key, 'site': site}

        email_user(self, 'emails/activation.txt',
                                        settings.DEFAULT_FROM_EMAIL, ctx_dict)


def post_login_actions(sender, user, request, **kwargs):
    """ After logging in, we want to show the user a message. """
    # We need to do this to make this work successfully in tests.
    # http://stackoverflow.com/questions/8930090/
    if not hasattr(request, 'user'):
        setattr(request, 'user', user)
    messages.success(request,
                        "You're now logged in as %s." % user.get_full_name())

# Register a post-login action for thing we want to do...
user_logged_in.connect(post_login_actions, dispatch_uid="user_logged_in")
