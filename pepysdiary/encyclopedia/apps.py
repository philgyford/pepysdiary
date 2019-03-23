from django.apps import AppConfig
from django.db.models import signals


class EncyclopediaConfig(AppConfig):
    name = 'pepysdiary.encyclopedia'

    def ready(self):
        from pepysdiary.common import signals