from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.news.models import Post

register = template.Library()

# Things that appear in the sidebar on several pages.


def put_in_block(html):
    "All sidebar content should be wrapped in this."
    return """<aside class="aside-block">
%s
</aside>
""" % html


@register.simple_tag
def email(*args):
    return put_in_block("""<h1>Email</h1>
<p><a href="http://feedburner.google.com/fb/a/mailverify?uri=PepysDiary&amp;loc=en_US">Receive diary entries by email daily</a></p>
""")


@register.simple_tag
def twitter(*args):
    return put_in_block("""<h1>Twitter</h1>
<p>Follow <a href="http://twitter.com/samuelpepys"><strong>@samuelpepys</strong></a> on Twitter for updates throughout the day</p>
""")

@register.simple_tag
def credit(*args):
    return put_in_block("""<p>This site is run by <a href="http://www.gyford.com/">Phil Gyford</a>.</p>
<p><a href="https://twitter.com/philgyford">@philgyford</a> on Twitter.</p>
""")


@register.simple_tag
def rss_feeds(*args):
    """
    Display a list of links to RSS feeds. Use something like:
        {% rss_feeds 'entries' 'posts' 'topics' %}
    Where the arguments are valid feed kinds from `rss_feed_link()`.
    Or do this, to display links to all possible feeds:
        {% rss_feeds %}
    """
    feeds = (
        ('entries', {
            'url': 'http://feeds.feedburner.com/PepysDiary',
            'things': 'Diary entries',
        }),
        ('topics', {
            'url': 'http://feeds.feedburner.com/PepysDiary-Encyclopedia',
            'things': 'Encyclopedia topics',
        }),
        ('articles', {
            'url': 'http://feeds.feedburner.com/PepysDiary-InDepthArticles',
            'things': 'In-Depth articles',
        }),
        ('posts', {
            'url': 'http://feeds.feedburner.com/PepysDiary-SiteNews',
            'things': 'Site News posts',
        }),
        # Not on Feedburner yet:
        # ('letters', {
        #     'url': 'http://feeds.feedburner.com/PepysDiary-SiteNews',
        #     'things': 'Site News posts',
        # }),
    )
    html = ''
    kinds = []
    # What feeds are we linking to?
    if len(args) == 0:
        kinds = [k for k, v in feeds]
    else:
        kinds = args

    feeds_dict = dict(feeds)
    for kind in kinds:
        if kind in feeds_dict:
            html += '<li class="feed"><a href="%s">%s</a></li>' % (
                        feeds_dict[kind]['url'], feeds_dict[kind]['things'])
    if html != '':
        html = put_in_block("""<h1>RSS feeds</h1>
<ul class="feeds">
%s
</ul>
""" % html)
    return html


def recent_list(queryset, title, date_format):
    """
    Generates a <dl> containing titles of posts, entries, articles, etc,
    linking to each one, with the date in its <dd>.

    queryset is the queryset of things to show.
    title is the text to use for the block's title.
    date_format is a date format suitable for strftime()
    """
    html = ''
    if queryset:
        for item in queryset:
            if hasattr(item, 'date_published'):
                # Posts and Articles.
                item_date = item.date_published
            else:
                item_date = item.date_created

            html += """<dt><a href="%s">%s</a></dt>
<dd>%s</dd>
""" % (item.get_absolute_url(),
        item.title,
        item_date.strftime(date_format))

        html = """<h1>%s</h1>
<dl class="dated">
%s
</dl>
""" % (title, html)
    return put_in_block(html)


@register.simple_tag(takes_context=True)
def latest_posts(context, quantity=5):
    """Displays links to the most recent Site News Posts."""
    post_list = Post.published_posts.all()[:quantity]
    return recent_list(post_list, 'Latest Site News',
                                        context['date_format_long_strftime'])


@register.simple_tag(takes_context=True)
def latest_articles(context, quantity=5):
    """Displays links to the most recent In-Depth Articles."""
    article_list = Article.published_articles.all()[:quantity]
    return recent_list(article_list, 'Latest In-Depth Articles',
                                        context['date_format_long_strftime'])


@register.simple_tag(takes_context=True)
def latest_topics(context, quantity=5):
    """Displays links to the most recent Encyclopedia Topics"""
    topic_list = Topic.objects.order_by('-date_created')[:quantity]
    return recent_list(topic_list, 'Latest Encyclopedia Topics',
                                        context['date_format_long_strftime'])


@register.simple_tag
def summary_year_navigation(current_year):
    """
    The list of years for the Diary Summary sidebar navigation.
    current_year will either be 'year' or a date object.
    """
    css_class = ''
    if current_year == 'before':
        css_class = 'active'
    else:
        current_year = current_year.year
    html = '<li class="%s"><a href="%s">Before the diary</a></li>' % (
                                                    css_class,
                                                    reverse('diary_summary'))
    for y in [1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669,]:
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
    return put_in_block('<ul class="nav nav-pills nav-stacked">%s</ul>' % html)


@register.simple_tag(takes_context=True)
def about_pages_links(context):
    """
    Used to build both the drop-down navigation menu and the list in the
    sidebar on About pages.
    Will highlight the correct link if there is a 'flatpage' in context.
    Returns HTML containing <li>s (no <ul>s).
    """
    # Mapping URL conf names to titles.
    # The titles should match the flatpages' titles in the Admin.
    # The links will be in this order:
    flatpages = (
        ('about', 'About this site'),
        ('about_text', 'About the text'),
        ('about_faq', 'FAQ'),
        ('about_annotations', 'Annotation guidelines'),
        ('about_formats', 'Email and RSS'),
        ('about_support', 'Supporting this site'),
    )
    links = []
    for page in flatpages:
        css_class = ''
        if 'flatpage' in context and context['flatpage'].title == page[1]:
            css_class = 'active'
        links.append('<li class="%s"><a href="%s">%s</a></li>' % (
                css_class,
                reverse(page[0]),
                page[1]
            ))
    return "\n".join(links)


@register.simple_tag
def family_tree_link(topic=None):
    """
    Displays a thumbnail of the family tree and a link to it.
    If `topic` is present, and the topic is featured on the family treet, then
    the text is different.
    """
    text = "See the Pepys family tree"
    if topic is not None and topic.on_pepys_family_tree:
        text = "See this person on the Pepys family tree"
    link_url = reverse('encyclopedia_familytree')

    return """
    <aside class="aside-block">
        <p><a href="%s"><img class="img-thumbnail" src="%simg/sidebar_family_tree.png" width="250" height="134" alt="Family tree thumbnail" />
        %s
        </a></p>
    </aside>
    """ % (link_url, settings.STATIC_URL, text)


@register.simple_tag
def category_map_link(category_id=None):
    """
    Displays a thumbnail of the category map and a link to it.
    If `category_id` is present, we link to that category's map.
    """
    if category_id is None:
        link_url = reverse('category_map')
        text = "See places from the Diary on a map"
    else:
        link_url = reverse('category_map', kwargs={'category_id': category_id})
        text = "See all places in this category on a map"
    return """
    <aside class="aside-block">
        <p><a href="%s"><img class="img-thumbnail" src="%simg/sidebar_category_map.png" width="250" height="134" alt="Map thumbnail" />
        %s
        </a></p>
    </aside>
    """ % (link_url, settings.STATIC_URL, text)
