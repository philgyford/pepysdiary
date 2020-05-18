from django.apps import AppConfig


class EncyclopediaConfig(AppConfig):
    name = "pepysdiary.news"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
