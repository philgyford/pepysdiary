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
        comment = super(AnnotationForm, self).clean_comment()

        # Replace three or more blank lines with two.
        comment = re.sub(
            r"""
            (
                (?:\r?\n)   # Match a single linebreak.
            )
            (?:[ \t]*          # 0 or more horizontal whitespace characters.
                (?:\r?\n)   # Another linebreak.
            )+              # And 1 or more of that lot.
        """,
            "\\1\\1",
            comment,
            re.MULTILINE | re.VERBOSE,
        )

        # Remove leading and trailing space:
        comment = comment.strip()

        return comment
