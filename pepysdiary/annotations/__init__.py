default_app_config = "pepysdiary.annotations.apps.AnnotationsConfig"


def get_model():
    from pepysdiary.annotations.models import Annotation

    return Annotation


def get_form():
    from pepysdiary.annotations.forms import AnnotationForm

    return AnnotationForm
