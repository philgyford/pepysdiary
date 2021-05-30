from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from django_comments.signals import comment_was_posted

from .models import Annotation
from .spam_checker import test_comment_for_spam


@receiver(post_save, sender=Annotation)
@receiver(post_delete, sender=Annotation)
def post_annotation_delete_actions(sender, instance, using, **kwargs):
    """
    If we're deleting a comment, we need to make sure the parent object's
    comment count and most-recent-comment date are still accurate.
    """
    instance.set_parent_comment_data()


comment_was_posted.connect(
    test_comment_for_spam, sender=Annotation, dispatch_uid="comments.post_comment"
)
