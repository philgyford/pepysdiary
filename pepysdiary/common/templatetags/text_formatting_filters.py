from django import template

register = template.Library()


@register.filter
def smartypants(value):
    try:
        import smartypants
        return smartypants.smartyPants(value)
    except ImportError:
        return value
