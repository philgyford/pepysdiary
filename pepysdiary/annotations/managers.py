from django.contrib.sites.models import Site

from django_comments.managers import CommentManager


class AnnotationManager(CommentManager):
    def get_queryset(self):
        """
        Trying this out, to fetch the related Persons for comments posted
        by authenticated users. Otherwise we're doing a query for every single
        comment while listing them.
        Suggested at http://stackoverflow.com/a/7992722/250962
        """
        return super().get_queryset().select_related("user")


class VisibleAnnotationManager(AnnotationManager):
    """
    For just displaying the public, non-removed annotations, eg on a person's
    profile page.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(site=Site.objects.get_current(), is_public=True, is_removed=False)
        )
