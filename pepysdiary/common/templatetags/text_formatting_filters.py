import re

import smartypants as original_smartypants
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def smartypants(value):
    """
    Modified of smartypants

    Handles some exceptions that don't use standard curly quotes.

    e.g. 'Change should not be ‘Change but ’Change.
    i.e. some words use a curly apostophe the other way.
    """
    replacements = (
        ("'Change", "&#8217;Change"),
        ("'Chequer", "&#8217;Chequer"),
        ("'guinny", "&#8217;guinny"),
        ("'light", "&#8217;light"),
        ("'lighting", "&#8217;lighting"),
        ("'prentice", "&#8217;prentice"),
        ("'Prentice", "&#8217;Prentice"),
        ("'prentices", "&#8217;prentices"),
        ("'sparagus", "&#8217;sparagus"),
    )
    for rep in replacements:
        value = re.sub(rf"(\W){rep[0]}(\W)", rf"\1{rep[1]}\2", value)

    # Set smartypants to use the default replacements, and replace with
    # unicode characters instead of HTML entities.
    attrs = original_smartypants.Attrs = (
        original_smartypants.Attr.set1 | original_smartypants.Attr.u
    )

    value = original_smartypants.smartypants(value, attrs)

    return value


@register.filter()
def markup_tooltip(value):
    if re.match(r"\d{4}-\d{4}", value) is not None:
        value = re.sub(
            r"^(\d{4})-(\d{4})",
            r'<span itemprop="birthDate">\1</span>-<span itemprop="deathDate">\2</span>',  # noqa: E501
            value,
        )
        value = mark_safe(value)

    return value
