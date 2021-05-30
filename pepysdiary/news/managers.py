from django.db import models


class PublishedPostManager(models.Manager):
    """
    All Posts that have been Published.
    """

    def get_queryset(self):
        from .models import Post

        return super().get_queryset().filter(status=Post.Status.PUBLISHED)
