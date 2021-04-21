from django.db import models


class PepysModel(models.Model):
    """
    All other Models should inherit this.
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # Does this item have 'comment's or 'annotation's?
    comment_name = "comment"

    class Meta:
        abstract = True

    @property
    def short_title(self):
        """
        Child models (eg, Diary Entries) might override this with a more
        bespoke way of generating a short version of its title.
        """
        if hasattr(self, "title"):
            return self.title
        else:
            return ""

    def get_a_comment_name(self):
        """
        If we want to print something like "an annotation" or "a comment",
        then call this.
        """
        if self.comment_name[:1] in [
            "a",
            "e",
            "h",
            "i",
            "o",
            "u",
        ]:
            return "an %s" % self.comment_name
        else:
            return "a %s" % self.comment_name
