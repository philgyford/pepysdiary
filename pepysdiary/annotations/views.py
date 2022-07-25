import django_comments
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django_comments.views.utils import next_redirect


@csrf_protect
@login_required
def flag(request, comment_id, next=None):
    """
    Flags a comment. Confirmation on GET, action on POST.

    Our replacement for the default
    https://github.com/django/django-contrib-comments/blob/master/django_comments/views/moderation.py#L15

    Because CommentFlags don't work with custom comments app, which
    is what we have with Annotations.

    Args:
    comment_id - The ID of the comment to flag
    next - Only used when POSTing, the URL to redirect to once done.

    Templates: :template:`comments/flag.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    comment = get_object_or_404(
        django_comments.get_model(),
        pk=comment_id,
        site__pk=get_current_site(request).pk,
    )

    # Flag on POST
    if request.method == "POST":
        perform_flag(request, comment)
        return next_redirect(
            request, fallback=next or "comments-flag-done", c=comment.pk
        )

    # Render a form on GET
    else:
        return render(request, "comments/flag.html", {"comment": comment, "next": next})


def perform_flag(request, comment):
    """Similarly, our replacement for the default
    https://github.com/django/django-contrib-comments/blob/master/django_comments/views/moderation.py#L99
    so it dirtily sends me an email, rather than create an actual
    CommentFlag.
    """

    comment_url = request.build_absolute_uri(comment.get_absolute_url())
    admin_url = reverse(
        "admin:%s_%s_change" % (comment._meta.app_label, comment._meta.model_name),
        args=[comment.id],
    )
    admin_url = request.build_absolute_uri(admin_url)

    message = """Flagged comment: {}

Admin:           {}

Flagged by:      {} <{}>
""".format(
        comment_url, admin_url, request.user.name, request.user.email
    )

    send_mail(
        "Pepys' Diary Flag",
        message,
        settings.COMMENT_FLAG_EMAIL,
        [settings.COMMENT_FLAG_EMAIL],
        fail_silently=False,
    )
