from django.apps import AppConfig


class DiaryConfig(AppConfig):
    name = "pepysdiary.diary"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
