import calendar

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.html import strip_tags

from pepysdiary.annotations.models import Annotation
from pepysdiary.common.utilities import smart_truncate
from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.letters.models import Letter
from pepysdiary.news.models import Post

register = template.Library()


def _commented_objects_list(context, title, quantity, model_class):
    """
    Passed a queryset of Entries, Topics, Articles, etc, it returns the context
    data for use with the common/inc/commented_objects_list.html template.
    """
    # Defaults, just in case we don't have these set in context:
    date_format = context.get("date_format_mid_strftime", "%d %b %Y")
    time_format = context.get("time_format_strftime", "%I:%M%p")

    queryset = model_class.objects.filter(last_comment_time__isnull=False).order_by(
        "-last_comment_time"
    )[:quantity]
    if queryset:
        template_context = {"comments": [], "title": title}
        ct = ContentType.objects.get_for_model(queryset[0])
        for obj in queryset:
            comment = Annotation.visible_objects.filter(
                object_pk=obj.pk, content_type_id=ct.id
            ).latest("submit_date")

            template_context["comments"].append(
                {
                    "data_time": calendar.timegm(comment.submit_date.timetuple()),
                    "date": comment.submit_date.strftime(date_format).lstrip("0"),
                    "iso_datetime": comment.submit_date.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "obj_title": obj.title,
                    "time": comment.submit_date.strftime(time_format)
                    .lstrip("0")
                    .lower(),
                    "text": strip_tags(smart_truncate(comment.comment, 70)),
                    "url": comment.get_absolute_url(),
                    "user_name": strip_tags(comment.get_user_name()),
                }
            )
        return template_context
    else:
        return None


@register.inclusion_tag("common/inc/commented_objects_list.html", takes_context=True)
def latest_commented_entries(context, title, quantity=5):
    """
    Displays a list of Diary Entries ordered by most recently-commented-on.
    """
    return _commented_objects_list(context, title, quantity, Entry)


@register.inclusion_tag("common/inc/commented_objects_list.html", takes_context=True)
def latest_commented_letters(context, title, quantity=5):
    """
    Displays a list of Letters ordered by most recently-commented-on.
    """
    return _commented_objects_list(context, title, quantity, Letter)


@register.inclusion_tag("common/inc/commented_objects_list.html", takes_context=True)
def latest_commented_topics(context, title, quantity=5):
    """
    Displays a list of Topics ordered by most recently-commented-on.
    """
    return _commented_objects_list(context, title, quantity, Topic)


@register.inclusion_tag("common/inc/commented_objects_list.html", takes_context=True)
def latest_commented_articles(context, title, quantity=5):
    """
    Displays a list of In-Depth Articles ordered by most recently-commented-on.
    """
    return _commented_objects_list(context, title, quantity, Article)


@register.inclusion_tag("common/inc/commented_objects_list.html", takes_context=True)
def latest_commented_posts(context, title, quantity=5):
    """
    Displays a list of Site News Posts ordered by most recently-commented-on.
    """
    return _commented_objects_list(context, title, quantity, Post)
