from django import template
from django.contrib.humanize.templatetags.humanize import ordinal

register = template.Library()


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
