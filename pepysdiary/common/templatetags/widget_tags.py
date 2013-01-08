from django import template
from django.core.urlresolvers import reverse

from pepysdiary.news.models import Post

register = template.Library()

# Things that appear in the sidebar on several pages.


def put_in_block(html):
    "All sidebar content should be wrapped in this."
    return '<div class="sidebar-block">%s</div>' % html


@register.simple_tag
def rss_feeds(*args):
    """
    Display a list of links to RSS feeds. Use something like:
        {% rss_feeds 'entries' 'posts' 'topics' %}
    Where the arguments are valid feed kinds from `rss_feed_link()`.
    """
    html = ''
    for kind in args:
        html += rss_feed_link(kind)
    if html != '':
        html = put_in_block('<ul class="feeds">%s</ul>' % html)
    return html


@register.simple_tag
def rss_feed_link(kind):
    """
    A single link in a list of RSS feeds.
    Probably not called directly now. Use `rss_feed_links()` instead.
    """
    feeds = {
        'articles': {
            'url': 'http://feeds.feedburner.com/PepysDiary-InDepthArticles',
            'things': 'In-Depth articles',
        },
        'entries': {
            'url': 'http://feeds.feedburner.com/PepysDiary',
            'things': 'Diary entries',
        },
        'posts': {
            'url': 'http://feeds.feedburner.com/PepysDiary-SiteNews',
            'things': 'Site News posts',
        },
        'topics': {
            'url': 'http://feeds.feedburner.com/PepysDiary-Encyclopedia',
            'things': 'Encyclopedia topics',
        },
        # Not on Feedburner yet:
        # 'letters': {
        #     'url': 'http://feeds.feedburner.com/PepysDiary-SiteNews',
        #     'things': 'Site News posts',
        # }
    }
    return '<li class="feed"><a href="%s">RSS feed of %s</a></li>' % (
                                    feeds[kind]['url'], feeds[kind]['things'])


@register.simple_tag(takes_context=True)
def latest_news(context, quantity=5):
    """Displays links to the most recent Site News Posts."""
    html = ''
    post_list = Post.published_posts.all()[:quantity]
    if post_list:
        for post in post_list:
            html += """ <dt><a href="%s">%s</a></dt>
<dd>%s</dd>
""" % (post.get_absolute_url(),
        post.title,
        post.date_published.strftime(context['date_format_long_strftime']))

        html = """<h4>Latest Site News</h4>
<dl>
%s</dl>
""" % html
    return put_in_block(html)


@register.simple_tag
def summary_year_navigation(current_year):
    """
    The list of years for the Diary Summary sidebar navigation.
    """
    css_class = ''
    if current_year == 'before':
        css_class = 'active'
    html = '<li class="%s"><a href="%s">Before the diary</a></li>' % (
                                                    css_class,
                                                    reverse('diary_summary'))
    for y in ['1660', '1661', '1662', '1663', '1664', '1665', '1666', '1667',
                                                            '1668', '1669', ]:
        css_class = ''
        if y == current_year:
            css_class = 'active'
        html += '<li class="%s"><a href="%s">%s</a></li>' % (
                        css_class,
                        reverse('summary_year_archive', kwargs={'year': y}),
                        y)
    html += '<li><a href="%s">After the diary (In-Depth Article)</a></li>' % (
                        reverse('article_detail', kwargs={
                            'year': '2012', 'month': '05', 'day': '31',
                            'slug': 'the-next-chapter'}
                        ))
    return put_in_block('<ul class="nav nav-tabs nav-stacked">%s</ul>' % html)
