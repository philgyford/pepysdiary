from django.contrib.comments.forms import CommentForm
from pepysdiary.annotations.models import Annotation


class AnnotationForm(CommentForm):

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return Annotation
