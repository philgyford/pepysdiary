import datetime

import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse

from .managers import PersonManager
from .utilities import email_user, validate_person_name


class Person(AbstractBaseUser, PermissionsMixin):
    """
    Our custom User class.
    No usernames - just `email` and `password`. Plus a unique `name` which is
    what the user wants to be known as.

    I ran this to translate my one User to a Person:

        INSERT INTO membership_person(id, name, email, password,
        last_login, is_superuser, is_staff, is_active, date_created,
        date_modified) SELECT id, username, email, password,
        last_login, is_superuser, is_staff, is_active, date_joined,
        date_joined FROM auth_user;

    And to make the Django 1.4 comments and flags work with the new Person
    model I did this:

        ALTER TABLE django_comments
            DROP CONSTRAINT django_comments_user_id_fkey;
        ALTER TABLE django_comments
            ADD CONSTRAINT django_comments_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES membership_person(id)
            DEFERRABLE INITIALLY DEFERRED;

        ALTER TABLE django_comment_flags
            DROP CONSTRAINT django_comment_flags_user_id_fkey;
        ALTER TABLE django_comment_flags
            ADD CONSTRAINT django_comment_flags_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES membership_person(id)
            DEFERRABLE INITIALLY DEFERRED;

    Note: I didn't have any existing comments/flags that were related to old
    User objects. If I did, that might all not have worked.
    """

    # The value that `activation_key` will be set to after the user has
    # activated their account.
    ACTIVATED = "ALREADY_ACTIVATED"

    # ALSO HAS:
    # password
    # last_login
    # is_superuser
    # user_permissions
    # groups

    email = models.EmailField(
        verbose_name="Email address",
        max_length=255,
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Publically visible name, spaces allowed",
        validators=[validate_person_name],
    )
    url = models.URLField(verbose_name="URL", max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(
        verbose_name="Is staff?",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        verbose_name="Is active?",
        default=False,
        help_text="Designates whether this user should be treated as "
        "active. Unselect this instead of deleting accounts.",
    )
    is_trusted_commenter = models.BooleanField(
        verbose_name="Is trusted commenter?",
        default=False,
        help_text="Allows them to post comments without spam-filtering",
    )
    activation_key = models.CharField(
        max_length=40,
        help_text="Will be 'ALREADY_ACTIVATED' when 'Is active?' is true.",
    )
    first_comment_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="First time they commented. Might be before the date they joined...",
    )
    date_activated = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = PersonManager()

    class Meta:
        verbose_name_plural = "People"

    def __str__(self):
        return self.name

    def get_full_name(self):
        "This is required by django-contrib-comments."
        return self.name

    def get_absolute_url(self):
        return reverse("profile", kwargs={"pk": self.pk})

    def get_summarised_topics(self):
        "A queryset of all the Topics the user has written summaries for"
        from pepysdiary.encyclopedia.models import Topic

        if self.topic_summaries.count() > 0:
            return self.topic_summaries.all().order_by("order_title")
        else:
            return Topic.objects.none()

    def get_indepth_articles(self):
        "A queryset of all the published Articles the user has written"
        from pepysdiary.indepth.models import Article

        if self.indepth_articles.count() > 0:
            return self.indepth_articles.filter(
                status=Article.Status.PUBLISHED
            ).order_by("date_published")
        else:
            return Article.objects.none()

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
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or (
            self.date_created + expiration_date <= datetime.datetime.now(pytz.utc)
        )

    # Not sure what this was ever for:
    # activation_key_expired.boolean = True

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
        ctx_dict = {"activation_key": self.activation_key, "site": site}

        email_user(
            self,
            "membership/emails/activation.txt",
            settings.DEFAULT_FROM_EMAIL,
            ctx_dict,
        )
