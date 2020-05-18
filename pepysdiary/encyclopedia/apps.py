from django.apps import AppConfig


class EncyclopediaConfig(AppConfig):
    name = "pepysdiary.encyclopedia"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
