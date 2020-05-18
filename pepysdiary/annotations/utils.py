from urllib.parse import urlencode
from urllib.request import Request, urlopen

import django
from django.conf import settings
from django.contrib import messages

from django.utils.encoding import smart_str

from django_comments import signals
from django_comments.models import CommentFlag
from pepysdiary.membership.models import Person


def is_akismet_spam(sender, comment, request, **kwargs):
    """
    Filter comments using Akismet.
    Much of this from Mezzanine:
    https://github.com/stephenmcd/mezzanine/blob/master/mezzanine/utils/views.py

    returns True if the comment was tested, and was thought to be spam.
    returns False if no testing happened, or if it's not spam.
    """
    if not hasattr(settings, "USE_SPAM_CHECK") or settings.USE_SPAM_CHECK is False:
        return False

    if comment.user and comment.user.is_trusted_commenter:
        return False

    if not settings.AKISMET_API_KEY:
        return False

    protocol = "http" if not request.is_secure() else "https"
    host = protocol + "://" + request.get_host()
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META["REMOTE_ADDR"])

    data = {
        "blog": host,
        "user_ip": ip,
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "referrer": request.POST.get("referrer", ""),
        "permalink": comment.get_content_object_url(),
        "comment_type": "comment",
        "comment_content": smart_str(comment.comment),
    }

    if comment.user:
        # Posted by a logged-in user.
        data["comment_author"] = comment.user.get_full_name()
        data["comment_author_email"] = comment.user.email
        if comment.user.url:
            data["comment_author_url"] = comment.user.url
    else:
        data["comment_author"] = comment.user_name
        data["comment_author_email"] = comment.user_email
        if comment.user_url:
            data["comment_author_url"] = comment.user_url

    # When testing you can ensure a spam response by adding this:
    # data['comment_author'] = 'viagra-test-123'

    api_url = "http://%s.rest.akismet.com/1.1/comment-check" % settings.AKISMET_API_KEY
    headers = {
        "User-Agent": "Django/%s | PepysDiary/1.0" % django.get_version(),
    }

    try:
        # Should return 'true' (is spam) or 'false' (not spam).
        response = urlopen(Request(api_url, urlencode(data), headers)).read()
    except Exception:
        return False
    return response == "true"


def test_comment_for_spam(sender, comment, request, **kwargs):
    """
    Tests a comment to see if it's spam.
    If so, adds a flag and marks it as not public.
    """
    if is_akismet_spam(sender, comment, request, **kwargs):
        # A flag has to be flagged by a person.
        # So we're just going to get the first superuser.
        user = Person.objects.filter(is_superuser=True, is_active=True)[0]
        # If we just do create() here then we get an error if this flagged spam
        # comment has identical content to a previously-flagged spam comment.
        # So this ensure we don't try and create duplicate flags:
        flag, created = CommentFlag.objects.get_or_create(
            user=user, comment=comment, flag="spam",
        )
        signals.comment_was_flagged.send(
            sender=comment.__class__,
            comment=comment,
            flag=flag,
            created=created,
            request=request,
        )
        comment.is_public = False
        comment.save()

        # Add a message which will be displayed in coment_form.html
        # (as well as wherever messages are usually displayed).
        # It will have tags like "spam warning".
        messages.warning(
            request,
            "Your post was flagged as possible spam. If it wasn't then "
            '<a href="mailto:%s?subject=Flagged annotation (ID: %s)">email me</a> '
            "to have it published." % (settings.MANAGERS[0][1], comment.id),
            extra_tags="spam",
        )
