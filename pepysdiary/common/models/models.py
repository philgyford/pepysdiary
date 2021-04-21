from django.contrib.sites.models import Site
from django.db import models

from .abstract import PepysModel
from ..managers import ConfigManager


class Config(PepysModel):
    """
    Site-wide configuration settings.
    """

    site = models.OneToOneField(Site, on_delete=models.SET_NULL, blank=False, null=True)
    allow_registration = models.BooleanField(default=True, blank=False, null=False)
    allow_login = models.BooleanField(default=True, blank=False, null=False)
    allow_comments = models.BooleanField(default=True, blank=False, null=False)

    use_registration_captcha = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="If checked, people must complete a Captcha field when registering.",
    )
    use_registration_question = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="If checked, people must successfully answer the question "
        "below when registering.",
    )
    registration_question = models.CharField(
        max_length=255, blank=True, null=False, default=""
    )
    registration_answer = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        default="",
        help_text="Not case-sensitive.",
    )

    objects = ConfigManager()
