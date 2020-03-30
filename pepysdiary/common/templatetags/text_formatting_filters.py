import re
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
    try:
        import smartypants

        replacements = (
            ("'Change", "&#8217;Change"),
            ("'Chequer", "&#8217;Chequer"),
            ("'light", "&#8217;light"),
            ("'prentice", "&#8217;prentice"),
            ("'prentices", "&#8217;prentices"),
        )
        for rep in replacements:
            value = re.sub(rf"(\W){rep[0]}(\W)", rf"\1{rep[1]}\2", value)

        return smartypants.smartypants(value)
    except ImportError:
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
