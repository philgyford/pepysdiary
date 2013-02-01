# coding: utf-8
import calendar

from django import template
from django.contrib.contenttypes.models import ContentType

from pepysdiary.annotations.models import Annotation
from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.letters.models import Letter
from pepysdiary.news.models import Post

register = template.Library()


def smart_truncate(content, length=80, suffix=u'…'):
    """Truncate a string at word boundaries."""
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0] + suffix


def commented_objects_list(model_class, context, title, quantity):
    """
    Passed a queryset of Entries, Topics, Articles, etc, it displays a <dl> of
    them, along with part of the most recent comment on each of them.
    """
    html = ''
    queryset = model_class.objects.filter(last_comment_time__isnull=False
                                    ).order_by('-last_comment_time')[:quantity]
    if queryset:
        ct = ContentType.objects.get_for_model(queryset[0])
        for obj in queryset:
            comment = Annotation.visible_objects.filter(object_pk=obj.pk,
                                                        content_type_id=ct.id
                                                    ).latest('submit_date')
            html += """
<dt class="newable" data-time="%(data_time)s"><a href="%(url)s"><strong>%(obj_title)s</strong></a> by <strong>%(user_name)s</strong> <small>on %(date)s at %(time)s</small></dt>
<dd>%(comment)s</dd>""" % {
        'data_time': calendar.timegm(comment.submit_date.timetuple()),
        'url': comment.get_absolute_url(),
        'obj_title': obj.title,
        'user_name': comment.get_user_name(),
        'date': comment.submit_date.strftime(
                                        context['date_format_mid_strftime']),
        'time': comment.submit_date.strftime(
                        context['time_format_strftime']).lstrip('0').lower(),
        'comment': smart_truncate(comment.comment, 80),
            }

        html = """<h4>%s</h4>
<dl class="recently-commented">
%s
</dl>
""" % (title, html)
    return html


@register.simple_tag(takes_context=True)
def latest_commented_entries(context, title, quantity=5):
    """
    Displays a <dl> of Diary Entries ordered by most recently-commented-on.
    """
    return commented_objects_list(Entry, context, title, quantity)


@register.simple_tag(takes_context=True)
def latest_commented_letters(context, title, quantity=5):
    """
    Displays a <dl> of Letters ordered by most recently-commented-on.
    """
    return commented_objects_list(Letter, context, title, quantity)


@register.simple_tag(takes_context=True)
def latest_commented_topics(context, title, quantity=5):
    """
    Displays a <dl> of Topics ordered by most recently-commented-on.
    """
    return commented_objects_list(Topic, context, title, quantity)


@register.simple_tag(takes_context=True)
def latest_commented_articles(context, title, quantity=5):
    """
    Displays a <dl> of In-Depth Articles ordered by most recently-commented-on.
    """
    return commented_objects_list(Article, context, title, quantity)


@register.simple_tag(takes_context=True)
def latest_commented_posts(context, title, quantity=5):
    """
    Displays a <dl> of Site News Posts ordered by most recently-commented-on.
    """
    return commented_objects_list(Post, context, title, quantity)
