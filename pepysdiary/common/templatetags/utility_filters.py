from django import template

register = template.Library()


@register.filter
def to_class_name(value):
    """
    Returns the class name of any object passed to it like:
    {{ obj|to_class_name }}
    """
    return value.__class__.__name__
