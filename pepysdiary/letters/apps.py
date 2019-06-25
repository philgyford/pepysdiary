from django.apps import AppConfig
from django.db.models import signals


class LettersConfig(AppConfig):
    name = 'pepysdiary.letters'

    def ready(self):
        from pepysdiary.common import signals