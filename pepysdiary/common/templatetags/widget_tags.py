from django import template

register = template.Library()


@register.simple_tag
def rss_feed_link(kind):
    feeds = {
        'diary': {
            'things': 'diary entries',
            'url': 'http://feeds.feedburner.com/PepysDiary',
        }
    }
    return '<li class="feed"><a href="%s">RSS feed of %s</a></li>' % (
                                    feeds[kind]['url'], feeds[kind]['things'])
