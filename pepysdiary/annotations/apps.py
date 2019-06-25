from django.apps import AppConfig
from django.db.models import signals


class AnnotationsConfig(AppConfig):
    name = 'pepysdiary.annotations'

    def ready(self):
        from pepysdiary.common import signals

