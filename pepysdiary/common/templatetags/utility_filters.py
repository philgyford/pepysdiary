import html
import re

from django import template
from django.contrib.humanize.templatetags.humanize import ordinal
from django.template.defaultfilters import truncatechars, urlize
from django.utils.safestring import mark_safe

register = template.Library()

URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)")

@register.filter
def to_class_name(value):
    """
    Returns the class name of any object passed to it like:
    {{ obj|to_class_name }}
    """
    return value.__class__.__name__


@register.filter
def ordinal_word(value):
    terms = {
        1: "first",
        2: "second",
        3: "third",
        4: "fourth",
        5: "fifth",
        6: "sixth",
        7: "seventh",
        8: "eighth",
        9: "ningth",
        10: "tenth",
    }

    if value in terms:
        return terms[value]
    else:
        return ordinal(value)


@register.filter
def custom_urlizetrunc(comment_text, chrs):
    """
    Finds URLs and escapes apostrophes (' -> %27), preventing urlize from breaking.
    Also removes 'http://' and 'https://' from the visible part of the URL for neatness.
    https://github.com/philgyford/pepysdiary/issues/867
    """
    escaped_comment = URL_PATTERN.sub(
        lambda m: m.group(0).replace("'", "%27"), comment_text
    )
    urlized_comment = urlize(escaped_comment)
    anchor_tags = re.findall(r"(<a [^>]*>)(.*?)(</a>)", urlized_comment)
    anchor_tags = list(set(anchor_tags)) # remove duplicates

    for opening_tag, inner_text, closing_tag in anchor_tags:
        cleaned_text = re.sub(r"^https?://", "", inner_text)

        # Decode HTML entities before truncation to ensure correct character count
        truncated_text = truncatechars(html.unescape(cleaned_text), chrs)

        urlized_comment = urlized_comment.replace(
            f"{opening_tag}{inner_text}{closing_tag}",
            f"{opening_tag}{truncated_text}{closing_tag}",
        )

    return mark_safe(urlized_comment)
