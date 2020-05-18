from django.apps import AppConfig


class IndepthConfig(AppConfig):
    name = "pepysdiary.indepth"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
