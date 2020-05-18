from django import template

register = template.Library()


@register.filter
def tabindex(value, index):
    """
    Add a tabindex attribute to the widget for a bound field.
    eg: {{ form.email|tabindex:3 }}
    """
    value.field.widget.attrs["tabindex"] = index
    return value
