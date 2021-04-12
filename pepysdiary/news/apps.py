from django.apps import AppConfig


class EncyclopediaConfig(AppConfig):
    name = "pepysdiary.news"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
