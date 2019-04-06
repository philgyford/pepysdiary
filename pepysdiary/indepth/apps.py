from django.apps import AppConfig
from django.db.models import signals


class IndepthConfig(AppConfig):
    name = 'pepysdiary.indepth'

    def ready(self):
        from pepysdiary.common import signals