import re

from django_comments.forms import CommentForm

from pepysdiary.annotations.models import Annotation


class AnnotationForm(CommentForm):
    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return Annotation

    def clean_comment(self):
        """
        Custom tidying of the comment text.
        """
        comment = super().clean_comment()

        # Replace three or more blank lines with two.
        comment = re.sub(r"\n\s*\n", "\n\n", comment)

        # Remove leading and trailing space:
        comment = comment.strip()

        return comment
