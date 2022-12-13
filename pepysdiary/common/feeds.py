import smartypants
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed, add_domain
from django.utils.encoding import force_str
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    Should be used as the feed_type for View classes that inherit Feed.
    """

    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
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

    def make_item_content_encoded(self, text1, text2, url, comment_name):
        """
        Called from item_content_encoded() in children.
        text1 and text2 are chunks of HTML text (or empty strings).
        url is the URL of the item (no domain needed, eg '/diary/1666/10/31/').
        comment_name is one of 'comment' or 'annotation'.
        """
        parts = []

        if text1 != "":
            parts.append(force_str(smartypants.smartypants(text1)))

        if text2 != "":
            parts.append(force_str(smartypants.smartypants(text2)))

        parts.append(
            '<p><strong><a href="%s#%ss">Read the %ss</a></strong></p>'
            % (
                add_domain(Site.objects.get_current().domain, url),
                comment_name,
                comment_name,
            )
        )

        html = " ".join(parts)

        # Newlines between HTML tags screw things up when an RSS feed item
        # is used as HTML content for an email. So we'll remove them all,
        # given this is HTML and newlines shouldn't affect any appearance.
        html = html.replace("\n", "").replace("\r", "")

        return html
