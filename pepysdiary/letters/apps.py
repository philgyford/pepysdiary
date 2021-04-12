from django.apps import AppConfig


class LettersConfig(AppConfig):
    name = "pepysdiary.letters"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
