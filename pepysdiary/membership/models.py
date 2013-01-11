from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,\
                                                                BaseUserManager
from django.db import models
from django.utils import timezone

from pepysdiary.membership.utilities import validate_person_name


class PersonManager(BaseUserManager):
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


class Person(AbstractBaseUser, PermissionsMixin):
    """
    Our custom User class.
    No usernames - just `email` and `password`. Plus a `name` which is what
    the user wants to be known as.

    I ran this to translate my one User to a Person:
    INSERT INTO membership_person(id, name, email, password, last_login, is_superuser, is_staff, is_active, date_created, date_modified) SELECT id, username, email, password, last_login, is_superuser, is_staff, is_active, date_joined, date_joined FROM auth_user;
    """
    email = models.EmailField(verbose_name='Email address', max_length=255,
                                                unique=True, db_index=True, )
    name = models.CharField(max_length=50, unique=True,
                        help_text="Publically visible name, spaces allowed",
                        validators=[validate_person_name])
    url = models.URLField(verbose_name='URL', max_length=255, blank=True,
                                                                    null=True)
    is_staff = models.BooleanField(verbose_name='Is staff?', default=False,
        help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(verbose_name='Is active?', default=True,
        help_text='Designates whether this user should be treated as '
                        'active. Unselect this instead of deleting accounts.')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name_plural = 'People'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __unicode__(self):
        return self.name
