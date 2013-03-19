# coding: utf-8
from django import template

from pepysdiary.events.models import DayEvent

register = template.Library()


@register.simple_tag
def events_for_day(date, exclude=None):
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

    html = ''
    for source_key, titles in events_by_source.items():
        if len(titles) > 0:
            # eg: '<h3>In Parliament</h3>'.
            html += u'<h3>%s</h3><ul>' % sources[source_key]

            for title, events in titles.items():
                # So, title is the string that all the events share.
                # events is now a list of DayEvent objects.
                if len(events) == 1:
                    # Only one event, so just list it.
                    if events[0].url == '':
                        html += u'<li>%s</li>' % (title)
                    else:
                        html += u'<li><a href="%s">%s</a></li>' % (
                                                        events[0].url, title)
                else:
                    # Many events with the same title. So show numbered links.
                    html += u'<li>%s: ' % title
                    for n, event in enumerate(events):
                        html += u'<a href="%s">%s</a> ' % (event.url, (n + 1))
                    html += '</li>'

            html += '</ul>'

    return html


@register.simple_tag
def events_for_day_in_sidebar(date, exclude=None):
    html = events_for_day(date, exclude)
    if html == '':
        return html
    else:
        return '<div class="sidebar-block"><h2>Also on this day</h2>%s</div>' % html
