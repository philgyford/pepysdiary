from django.apps import AppConfig
from django.db.models import signals


class DiaryConfig(AppConfig):
    name = 'pepysdiary.diary'

    def ready(self):
        from pepysdiary.common import signals