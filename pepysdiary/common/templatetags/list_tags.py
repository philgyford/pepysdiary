# coding: utf-8
import calendar

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.html import mark_safe, strip_tags

from pepysdiary.annotations.models import Annotation
from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.letters.models import Letter
from pepysdiary.news.models import Post

register = template.Library()


def smart_truncate(content, length=80, suffix='…'):
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
<article class="media newable media-small" data-time="%(data_time)s">
    <span class="newflag pull-left" aria-hidden="true" title="New since your last visit">✹</span>
    <span class="sr-only">New since your last visit</span>
    <div class="media-body">
        <h2 class="media-heading">
            <span class="comment-title">
                <a href="%(url)s">%(obj_title)s</a>
            </span>
            by
            <span class="comment-name">
                %(user_name)s
            </span>
            <small>
                <time class="timeago" datetime="%(iso_datetime)s">on %(date)s</time>
            </small>
        </h2>
        <p class="text-muted">%(comment)s</p>
    </div>
</article>
""" % {
        'data_time': calendar.timegm(comment.submit_date.timetuple()),
        'url': comment.get_absolute_url(),
        'obj_title': obj.title,
        'user_name': strip_tags(comment.get_user_name()),
        'iso_datetime': comment.submit_date.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'date': comment.submit_date.strftime(
                                        context['date_format_mid_strftime']),
        'time': comment.submit_date.strftime(
                        context['time_format_strftime']).lstrip('0').lower(),
        'comment': strip_tags(smart_truncate(comment.comment, 70)),
            }

        html = """<section class="recently-commented">
<header>
    <h1 class="h2">%s</h1>
</header>
%s
</section>
<hr>
""" % (title, html)
    return html


@register.simple_tag(takes_context=True)
def latest_commented_entries(context, title, quantity=5):
    """
    Displays a <dl> of Diary Entries ordered by most recently-commented-on.
    """
    return mark_safe(commented_objects_list(Entry, context, title, quantity))


@register.simple_tag(takes_context=True)
def latest_commented_letters(context, title, quantity=5):
    """
    Displays a <dl> of Letters ordered by most recently-commented-on.
    """
    return mark_safe(commented_objects_list(Letter, context, title, quantity))


@register.simple_tag(takes_context=True)
def latest_commented_topics(context, title, quantity=5):
    """
    Displays a <dl> of Topics ordered by most recently-commented-on.
    """
    return mark_safe(commented_objects_list(Topic, context, title, quantity))


@register.simple_tag(takes_context=True)
def latest_commented_articles(context, title, quantity=5):
    """
    Displays a <dl> of In-Depth Articles ordered by most recently-commented-on.
    """
    return mark_safe(commented_objects_list(Article, context, title, quantity))


@register.simple_tag(takes_context=True)
def latest_commented_posts(context, title, quantity=5):
    """
    Displays a <dl> of Site News Posts ordered by most recently-commented-on.
    """
    return mark_safe(commented_objects_list(Post, context, title, quantity))

