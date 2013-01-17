import re

from django.contrib.comments.forms import CommentForm
from pepysdiary.annotations.models import Annotation


class AnnotationForm(CommentForm):

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return Annotation

    def clean_comment(self):
        """
        Custom validation.
        """
        comment = super(AnnotationForm, self).clean_comment()
        # Replace multiple linebreaks with single ones.
        comment = re.sub(r'(\r?\n){2,}', '\\1', comment, re.MULTILINE)
        # Remove leading and trailing space:
        comment = comment.strip()
        return comment


