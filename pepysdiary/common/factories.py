import factory
from django.contrib.sites.models import Site

from .models import Config


class ConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Config

    site = Site.objects.get_current()
