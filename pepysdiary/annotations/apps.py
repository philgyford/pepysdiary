from django.apps import AppConfig


class AnnotationsConfig(AppConfig):
    name = "pepysdiary.annotations"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
