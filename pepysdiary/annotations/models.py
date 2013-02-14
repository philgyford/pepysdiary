from django.contrib.comments.managers import CommentManager
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.utils.html import strip_tags

from pepysdiary.annotations.utils import test_comment_for_spam


class AnnotationManager(CommentManager):
    def get_query_set(self):
        """
        Trying this out, to fetch the related Persons for comments posted
        by authenticated users. Otherwise we're doing a query for every single
        comment while listing them.
        Suggested at http://stackoverflow.com/a/7992722/250962
        """
        return super(AnnotationManager, self).get_query_set().select_related(
                                                                        'user')


class VisibleAnnotationManager(AnnotationManager):
    """
    For just displaying the public, non-removed annotations, eg on a person's
    profile page.
    """
    def get_query_set(self):
        return super(VisibleAnnotationManager, self).get_query_set().filter(
                                               site=Site.objects.get_current(),
                                               is_public=True,
                                               is_removed=False)


class Annotation(Comment):

    objects = AnnotationManager()
    visible_objects = VisibleAnnotationManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # We don't allow HTML at all:
        self.comment = strip_tags(self.comment)

        super(Annotation, self).save(*args, **kwargs)
        self._set_parent_comment_data()
        self._set_user_first_comment_date()

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

    def _set_parent_comment_data(self):
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
                    u"Content type %(ct_id)s object has no associated model" %
                                           {'ct_id': self.content_type_id})
            obj = content_type.get_object_for_this_type(pk=self.object_pk)
        except (ObjectDoesNotExist, ValueError):
            raise AttributeError(
                u"Content type %(ct_id)s object %(obj_id)s doesn't exist" %
                   {'ct_id': self.content_type_id, 'obj_id': self.object_pk})

        # All good. So set the count of visible comments.
        # Note: We explicitly remove any ordering because we don't need it
        # and it should speed things up.
        qs = Annotation.objects.filter(content_type__pk=self.content_type_id,
                                        object_pk=self.object_pk,
                                        site=self.site,
                                        is_public=True,
                                        is_removed=False).order_by()
        obj.comment_count = qs.count()

        # We also need to set the last_comment_time on the object.
        if obj.comment_count == 0:
            # No comments (this comment must be invisible).
            # So make sure the comment time is None.
            obj.last_comment_time = None
        else:
            # There are some comments on this object...
            if self.is_public == True and self.is_removed == False and \
                (obj.last_comment_time is None or \
                    self.submit_date > obj.last_comment_time):
                # This is the most recent public comment, so:
                obj.last_comment_time = self.submit_date
            else:
                # This isn't the most recent public comment, so:
                obj.last_comment_time = qs.aggregate(Max('submit_date'))[
                                                            'submit_date__max']

        obj.save()

    def _set_user_first_comment_date(self):
        """
        For each Person we store the date they posted their first comment.
        So we check to see if the user's first comment, and set the date if so.
        (There's a chance that the user might already have a first_comment_date
        which is after this Annotation's date, eg, during importing old
        comments. So we test for that too.)
        """
        if self.user.first_comment_date is None or\
                            self.user.first_comment_date > self.submit_date:
            self.user.first_comment_date = self.submit_date
            self.user.save()


comment_was_posted.connect(
    test_comment_for_spam,
    sender=Annotation,
    dispatch_uid='comments.post_comment',
)
