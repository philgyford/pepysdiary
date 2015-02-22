from django import template

register = template.Library()


@register.filter
def smartypants(value):
    try:
        import smartypants
        return smartypants.smartypants(value)
    except ImportError:
        return value
