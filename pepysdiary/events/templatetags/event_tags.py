# coding: utf-8
from django import template
from django.core.urlresolvers import reverse

from pepysdiary.diary.models import Entry
from pepysdiary.events.models import DayEvent
from pepysdiary.letters.models import Letter

register = template.Library()


def events_html(title, event_list):
    """
    Generates the HTML for a list of Diary Entries, Letters or DayEvents.
    `title` is for the <h2>, eg 'Diary Entries' or 'In Parliament'.
    `event_list` is a list of dicts, each dict having a `text` element and an
    optional `url`.
    """
    if len(event_list) == 0:
        return ''
    html = u"<h2>%s</h2>\n<ul>\n" % title
    for li in event_list:
        if 'url' in li and li['url'] != '':
            html += u"<li><a href=\"%s\">%s</a></li>\n" % (
                                                        li['url'], li['text'])
        else:
            html += u"<li>%s</li>\n" % li['text']
    html += "</ul>\n"
    return html


def entries_for_day(date):
    """
    Returns HTML for links to any Diary Entries that were written on `date`.
    Or an empty string if there aren't any.
    """
    event_list = []
    entries = Entry.objects.filter(diary_date=date)
    if len(entries) > 0:
        for entry in entries:
            event_list.append({'url': entry.get_absolute_url(),
                                'text': entry.title})
    return events_html('Diary Entries', event_list)


def letters_for_day(date):
    """
    Returns HTML for links to any Letters that were written on `date`.
    Or an empty string if there aren't any.
    """
    event_list = []
    letters = Letter.objects.filter(letter_date=date)
    if len(letters) > 0:
        for letter in letters:
            event_list.append({'url': letter.get_absolute_url(),
                                'text': letter.title})
    return events_html('Letters', event_list)


def dayevents_for_day(date):
    """
    Returns HTML for displaying any DayEvents that happen on `date`.
    Or an empty string if there aren't any.
    """
    html = ''

    sources = {key: label for (key, label) in DayEvent.SOURCE_CHOICES}

    # Makes a dict like:
    # {10: {}, 20: {}, 30: {}}
    events_by_source = {key: {} for (key, label) in DayEvent.SOURCE_CHOICES}

    for ev in DayEvent.objects.filter(event_date=date).order_by('source'):
        # For each source, there *might* be several events with the same title
        # so we create a list of events for each title, within each source.
        if ev.title not in events_by_source[ev.source]:
            events_by_source[ev.source][ev.title] = []
        events_by_source[ev.source][ev.title].append(ev)

    for source_key, titles in events_by_source.items():
        if len(titles) > 0:
            event_list = []
            for title, events in titles.items():
                # So, title is the string that all the events share.
                # events is now a list of DayEvent objects.
                if len(events) == 1:
                    # Only one event, so just list it.
                    event_list.append({'url': events[0].url,
                                        'text': events[0].title})
                else:
                    # Many events with the same title. So show numbered links.
                    event_html = u'%s: ' % title
                    for n, event in enumerate(events):
                        event_html += u'<a href="%s">%s</a> ' % (
                                                            event.url, (n + 1))
                    event_list.append({'text': event_html})

            # Make the HTML. sources[source_key] is like 'In Parliament'.
            html += events_html(sources[source_key], event_list)

    if html != '':
        html += '<p class="text-right"><small><a href="%s#on-this-day">About these events</a></small></p>' % (
            reverse('django.contrib.flatpages.views.flatpage',
                    kwargs={'url': '/about/text/'})
        )

    return html


@register.simple_tag
def events_for_day(date, exclude=None):
    html = ''
    if exclude != 'entries':
        html += entries_for_day(date)
    if exclude != 'letters':
        html += letters_for_day(date)
    html += dayevents_for_day(date)
    return html


@register.simple_tag
def events_for_day_in_sidebar(date, exclude=None):
    html = events_for_day(date, exclude)
    if html == '':
        return html
    else:
        return """<aside class="aside-block">
    <header class="aside-header">
        <h1 class="aside-title">Also on this day</h1>
    </header>
    <div class="aside-body">
%s
    </div>
</aside>
""" % html
