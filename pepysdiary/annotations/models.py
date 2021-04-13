from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, signals
from django.dispatch import receiver
from django.utils.html import strip_tags

from django_comments.abstracts import CommentAbstractModel
from django_comments.managers import CommentManager
from django_comments.signals import comment_was_posted

from pepysdiary.annotations.utils import test_comment_for_spam


class AnnotationManager(CommentManager):
    def get_queryset(self):
        """
        Trying this out, to fetch the related Persons for comments posted
        by authenticated users. Otherwise we're doing a query for every single
        comment while listing them.
        Suggested at http://stackoverflow.com/a/7992722/250962
        """
        return super(AnnotationManager, self).get_queryset().select_related("user")


class VisibleAnnotationManager(AnnotationManager):
    """
    For just displaying the public, non-removed annotations, eg on a person's
    profile page.
    """

    def get_queryset(self):
        return (
            super(VisibleAnnotationManager, self)
            .get_queryset()
            .filter(site=Site.objects.get_current(), is_public=True, is_removed=False)
        )


class Annotation(CommentAbstractModel):
    """
    Fields inherited from CommentAbstractModel:

    content_type = ForeignKey to django.contrib.contenttypes.models.ContentType
    object_pk = CharField
    content_object = django.contrib.contenttypes.fields.GenericForeignKey
    site = ForeignKey to django.contrib.sites.modelsSite
    user - ForeignKey to membership.Person
    user_name - CharField
    user_email - EmailField
    user_url - URLField
    comment - TextField
    submit_date - DateTimeField
    ip_address - GenericIPAddressField
    is_public - BooleanField (comment is effectively entirely deleted)
    is_removed - BooleanField (comment is inappropriate; displays "has been removed")
    """

    # Also see index_components() method.
    search_document = SearchVectorField(null=True)

    objects = AnnotationManager()
    visible_objects = VisibleAnnotationManager()

    class Meta:
        ordering = ("submit_date",)
        permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = "annotation"
        verbose_name_plural = "annotations"
        indexes = [GinIndex(fields=["search_document"])]

    def save(self, *args, **kwargs):
        # We don't allow HTML at all:
        self.comment = strip_tags(self.comment)

        super(Annotation, self).save(*args, **kwargs)
        self.set_parent_comment_data()
        self._set_user_first_comment_date()

    def index_components(self):
        """Used by common.signals.on_save() to update the SearchVector on
        self.search_document.
        """
        return ((self.comment, "A"),)

    def get_user_name(self):
        """
        Now:
        The name saved when the comment was posted.

        Formerly:
        If posted by a user account, return that user's current name, else
        return the name supplied when the comment was posted.
        """
        # if self.user:
        #     return self.user.get_full_name()
        # else:
        #     return self.user_name
        return self.user_name

    def get_user_email(self):
        """
        If posted by a user account, return that user's current email, else
        return the email supplied when the comment was posted.
        """
        if self.user:
            return self.user.email
        else:
            return self.user_email

    def get_user_url(self):
        """
        If posted by a user account, return that user's current url, else
        return the url supplied when the comment was posted.
        """
        if self.user:
            return self.user.url
        else:
            return self.user_url

    def set_parent_comment_data(self):
        """
        We store the comment_count for each object that can have comments.
        So here we set the comment_count after we save each comment.
        Which should take account of comments being added, removed, flagged
        etc.

        We also have to ensure the parent object's last_comment_time is
        still accurate.
        """

        # Make sure the content_type and object for this Annotation exist.
        # This is adapted from django.contrib.contenttypes.views.shortcut().
        try:
            content_type = ContentType.objects.get(pk=self.content_type_id)
            if not content_type.model_class():
                raise AttributeError(
                    "Content type %(ct_id)s object has no associated model"
                    % {"ct_id": self.content_type_id}
                )
            obj = content_type.get_object_for_this_type(pk=self.object_pk)
        except (ObjectDoesNotExist, ValueError):
            raise AttributeError(
                "Content type %(ct_id)s object %(obj_id)s doesn't exist"
                % {"ct_id": self.content_type_id, "obj_id": self.object_pk}
            )

        # All good. So set the count of visible comments.
        # Note: We explicitly remove any ordering because we don't need it
        # and it should speed things up.
        qs = Annotation.objects.filter(
            content_type__pk=self.content_type_id,
            object_pk=self.object_pk,
            site=self.site,
            is_public=True,
            is_removed=False,
        ).order_by()
        obj.comment_count = qs.count()

        # We also need to set the last_comment_time on the object.
        if obj.comment_count == 0:
            # No comments (this comment must be invisible).
            # So make sure the comment time is None.
            obj.last_comment_time = None
        else:
            # There are some comments on this object...
            if (
                self.is_public is True
                and self.is_removed is False
                and (
                    obj.last_comment_time is None
                    or self.submit_date > obj.last_comment_time
                )
            ):
                # This is the most recent public comment, so:
                obj.last_comment_time = self.submit_date
            else:
                # This isn't the most recent public comment, so:
                obj.last_comment_time = qs.aggregate(Max("submit_date"))[
                    "submit_date__max"
                ]

        obj.save()

    def _set_user_first_comment_date(self):
        """
        For each Person we store the date they posted their first comment.
        So we check to see if the user's first comment, and set the date if so.
        (There's a chance that the user might already have a first_comment_date
        which is after this Annotation's date, eg, during importing old
        comments. So we test for that too.)
        """
        # So, if this annotation has a user, and is visible:
        if (
            self.user is not None
            and self.is_public is True
            and self.is_removed is False
        ):
            # And if this annotation is earlier than the user's
            # first_comment_date:
            if (
                self.user.first_comment_date is None
                or self.submit_date < self.user.first_comment_date
            ):
                self.user.first_comment_date = self.submit_date
                self.user.save()


@receiver(signals.post_delete, sender=Annotation)
def post_annotation_delete_actions(sender, instance, using, **kwargs):
    """
    If we're deleting a comment, we need to make sure the parent object's
    comment count and most-recent-comment date are still accurate.
    """
    instance.set_parent_comment_data()


comment_was_posted.connect(
    test_comment_for_spam, sender=Annotation, dispatch_uid="comments.post_comment"
)
