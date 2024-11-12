from django import template
from django.urls import reverse
from django.utils.html import mark_safe

from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia import topic_lookups
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.indepth.models import Article
from pepysdiary.news.models import Post

register = template.Library()

# Things that appear in the sidebar or footer on several pages.


@register.inclusion_tag("common/widgets/credit.html")
def credit():
    return {}


@register.inclusion_tag("common/widgets/diary_emails.html")
def diary_emails():
    return {}


@register.inclusion_tag("common/widgets/discussion_group.html")
def discussion_group():
    return {}


@register.inclusion_tag("common/widgets/socials.html")
def socials():
    return {}


@register.inclusion_tag("common/widgets/support.html")
def support():
    return {}


@register.inclusion_tag("common/widgets/rss_feeds.html")
def rss_feeds(*args):
    """
    Display a list of links to RSS feeds. Use something like:
        {% rss_feeds 'entries' 'posts' 'topics' %}
    Where the arguments are valid feed kinds from `rss_feed_link()`.
    Or do this, to display links to all possible feeds:
        {% rss_feeds %}
    """
    feeds = (
        (
            "entries",
            {
                "url": "https://feeds.feedburner.com/PepysDiary",
                "title": "Diary entries",
            },
        ),
        (
            "topics",
            {
                "url": "https://feeds.feedburner.com/PepysDiary-Encyclopedia",
                "title": "Encyclopedia topics",
            },
        ),
        (
            "articles",
            {
                "url": "https://feeds.feedburner.com/PepysDiary-InDepthArticles",
                "title": "In-Depth articles",
            },
        ),
        (
            "posts",
            {
                "url": "https://feeds.feedburner.com/PepysDiary-SiteNews",
                "title": "Site News posts",
            },
        ),
        # Not on Feedburner yet:
        # ('letters', {
        #     'url': 'https://feeds.feedburner.com/PepysDiary-SiteNews',
        #     'title': 'Site News posts',
        # }),
    )
    kinds = []
    # What feeds are we linking to?
    kinds = [k for k, v in feeds] if len(args) == 0 else args

    feeds_dict = dict(feeds)

    feeds = []
    for kind in kinds:
        if kind in feeds_dict:
            feeds.append(feeds_dict[kind])

    return {"feeds": feeds}


@register.inclusion_tag("common/widgets/recent_list.html", takes_context=True)
def latest_posts(context, quantity=5):
    """
    Displays links to the most recent Site News Posts.
    Expects date_format_long to be in the context.
    """
    post_list = Post.published_posts.all().only("title", "date_published")[:quantity]

    return {
        "object_list": post_list,
        "title": "Latest Site News",
        "date_format_long": context["date_format_long"],
    }


@register.inclusion_tag("common/widgets/recent_list.html", takes_context=True)
def latest_articles(context, quantity=5):
    """
    Displays links to the most recent In-Depth Articles.
    Expects date_format_long to be in the context.
    """
    article_list = Article.published_articles.all().only(
        "title", "date_published", "slug"
    )[:quantity]
    return {
        "object_list": article_list,
        "title": "Latest In-Depth Articles",
        "date_format_long": context["date_format_long"],
    }


@register.inclusion_tag("common/widgets/recent_list.html", takes_context=True)
def latest_topics(context, quantity=5):
    """Displays links to the most recent Encyclopedia Topics"""
    topic_list = Topic.objects.order_by("-date_created").only("title", "date_created")[
        :quantity
    ]
    return {
        "object_list": topic_list,
        "title": "Latest Encyclopedia Topics",
        "date_format_long": context["date_format_long"],
    }


@register.inclusion_tag("common/widgets/all_articles.html", takes_context=True)
def all_articles(context, exclude_id=None):
    """
    Displays links to all the In-Depth Articles.
    If `exclude_id` is set, then we include that Article, but don't link to it.
    """
    article_list = Article.published_articles.all().only(
        "title", "date_published", "slug"
    )
    return {
        "article_list": article_list,
        "exclude_id": exclude_id,
        "date_format_long": context["date_format_long"],
    }


@register.simple_tag
def summary_year_navigation(current_year):
    """
    The list of years for the Diary Summary sidebar navigation.
    current_year will either be 'before' (to indicate we're on the
    "Before the diary" summary page) or a python date object.
    """
    css_class = ""

    if current_year == "before":
        css_class = "active"
    else:
        current_year = current_year.year

    href = reverse("diary_summary")
    html = f'<a class="list-group-item {css_class}" href="{href}">Before the diary</a>'

    for y in Entry.objects.all_years():
        css_class = ""
        if int(y) == current_year:
            css_class = "active"
        href = reverse("summary_year_archive", kwargs={"year": y})
        html += f'<a class="list-group-item {css_class}" href="{href}">{y}</a>'

    href = reverse(
        "article_detail",
        kwargs={
            "year": "2012",
            "month": "05",
            "day": "31",
            "slug": "the-next-chapter",
        },
    )
    html += (
        f'<a class="list-group-item" href="{href}">' "After the diary (in Articles)</a>"
    )
    return mark_safe(f'<div class="list-group">{html}</div>')


@register.inclusion_tag("common/widgets/family_tree_link.html")
def family_tree_link(topic=None):
    """
    Displays a thumbnail of the family tree and a link to it.
    If `topic` is present, and the topic is featured on the family tree, then
    the text is different.

    topic should be a Topic object, or None.
    """
    link_text = "See the Pepys family tree"
    if topic is not None and topic.on_pepys_family_tree:
        link_text = mark_safe("See this person on the Pepys family&nbsp;tree")
    return {"link_text": link_text}


@register.inclusion_tag("common/widgets/pepys_wealth_link.html")
def pepys_wealth_link():
    """
    Displays a thumbnail of the Pepys' Wealth chart and a link to it.
    """
    link_text = "See his wealth during the diary"
    link_url = reverse("topic_detail", kwargs={"pk": topic_lookups.PEPYS_WEALTH})
    return {"link_url": link_url, "link_text": link_text}


@register.inclusion_tag("common/widgets/category_map_link.html")
def category_map_link(category_id=None):
    """
    Displays a thumbnail of the category map and a link to it.
    If `category_id` is present, we link to that category's map.
    """
    if category_id is None:
        link_url = reverse("category_map")
        link_text = mark_safe("See places from the Diary on a&nbsp;map")
    else:
        link_url = reverse("category_map", kwargs={"category_id": category_id})
        link_text = mark_safe("See all places in this category on one&nbsp;map")

    return {"link_url": link_url, "link_text": link_text}


@register.simple_tag
def admin_link_change(url):
    return mark_safe(
        f"""<p class="admin-links"><a class="admin" href="{url}">Edit</a></p>"""
    )


@register.inclusion_tag("common/widgets/detailed_topics.html")
def detailed_topics():
    topics = (
        (150, "Elizabeth Pepys"),
        (112, "Sir Edward Mountagu (Pepys’ patron)"),
        (2381, "Catherine of Braganza (Queen)"),
        (5036, "Frances Stuart (Duchess of Richmond)"),
        (1062, "Barbara Palmer (Countess of Castlemaine)"),
        (370, "17th Century Mathematics"),
        (5344, "John Wilmot (2nd Earl of Rochester)"),
        (804, "Sir Edward Hyde (Earl of Clarendon)"),
        (1686, "Sir Charles Berkeley"),
        (1018, "Sir George Carteret"),
    )
    return {"topics": topics}
