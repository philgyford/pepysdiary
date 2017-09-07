import re   
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def smartypants(value):
    try:
        import smartypants
        return smartypants.smartypants(value)
    except ImportError:
        return value

@register.filter()
def markup_tooltip(value):
    if re.match('\d{4}-\d{4}', value) is not None:
        value = re.sub(r'^(\d{4})-(\d{4})',
                    r'<span itemprop="birthDate">\1</span>-<span itemprop="deathDate">\2</span>',
                    value)
        value = mark_safe(value)

    return value

