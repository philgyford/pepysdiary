from django.contrib.sites.models import Site
from django.db import models


class PepysModel(models.Model):
    """
    All other Models should inherit this.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Config(PepysModel):
    """
    Site-wide configuration settings.
    """
    site = models.OneToOneField(Site, blank=False, null=False)
    allow_registration = models.BooleanField(default=True, blank=False,
                                                                    null=False)
    allow_login = models.BooleanField(default=True, blank=False, null=False)
    allow_comments = models.BooleanField(default=True, blank=False, null=False)
