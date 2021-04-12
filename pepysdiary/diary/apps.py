from django.apps import AppConfig


class DiaryConfig(AppConfig):
    name = "pepysdiary.diary"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
