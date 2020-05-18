from django.apps import AppConfig


class LettersConfig(AppConfig):
    name = "pepysdiary.letters"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
