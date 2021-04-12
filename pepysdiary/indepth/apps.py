from django.apps import AppConfig


class IndepthConfig(AppConfig):
    name = "pepysdiary.indepth"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from pepysdiary.common import signals  # noqa: F401
