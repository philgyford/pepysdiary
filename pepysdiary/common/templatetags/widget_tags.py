from django import template

register = template.Library()


@register.simple_tag
def rss_feed_link(kind):
    feeds = {
        'entries': {
            'url': 'http://feeds.feedburner.com/PepysDiary',
            'things': 'Diary entries',
        },
        'posts': {
            'url': 'http://feeds.feedburner.com/PepysDiary-SiteNews',
            'things': 'Site News posts',
        }
    }
    return '<li class="feed"><a href="%s">RSS feed of %s</a></li>' % (
                                    feeds[kind]['url'], feeds[kind]['things'])
