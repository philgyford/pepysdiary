from django.apps import AppConfig


class AnnotationsConfig(AppConfig):
    name = "pepysdiary.annotations"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
