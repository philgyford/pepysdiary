from django.db import models


class PublishedArticleManager(models.Manager):
    """
    All Articles that have been Published.
    """

    def get_queryset(self):
        from .models import Article

        return super().get_queryset().filter(status=Article.Status.PUBLISHED)
