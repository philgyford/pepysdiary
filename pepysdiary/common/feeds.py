from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed, add_domain
from django.utils.encoding import force_str
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags

from pepysdiary.common.templatetags.text_formatting_filters import smartypants


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    Should be used as the feed_type for View classes that inherit Feed.
    """

    def root_attributes(self):
        attrs = super().root_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement("content:encoded", item["content_encoded"])


class BaseRSSFeed(Feed):
    feed_type = ExtendedRSSFeed

    link = "/"
    # Children should also have:
    # title
    # description

    def item_extra_kwargs(self, item):
        return {"content_encoded": self.item_content_encoded(item)}

    def item_title(self, item):
        return force_str(item.title)

    def item_pubdate(self, item):
        return item.date_published

    def item_author_name(self, item):
        return "Phil Gyford"

    def make_item_description(self, text):
        "Called by item_description() in children."
        length = 250
        text = strip_tags(text)
        if len(text) <= length:
            return force_str(text)
        else:
            return " ".join(text[: length + 1].split(" ")[0:-1]) + "..."

    def make_item_content_encoded(self, texts, url, comment_name):
        """
        Called from item_content_encoded() in children.

        Arguments:
        - texts - chunks of HTML text (or empty strings).
        - url - the URL of the item (no domain needed, eg '/diary/1666/10/31/').
        - comment_name - one of 'comment' or 'annotation'.
        """
        parts = []

        for text in texts:
            if text != "":
                parts.append(force_str(smartypants(text)))

        url = add_domain(
            Site.objects.get_current().domain,
            url,
            secure=settings.PEPYS_USE_HTTPS,
        )
        parts.append(
            f'<p><strong><a href="{url}#{comment_name}s">'
            f"Read the {comment_name}s</a></strong></p>"
        )

        html = " ".join(parts)

        # Newlines between HTML tags screw things up when an RSS feed item
        # is used as HTML content for an email. So we'll remove them all,
        # given this is HTML and newlines shouldn't affect any appearance.
        html = html.replace("\n", "").replace("\r", "")

        return html
