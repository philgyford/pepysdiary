from django import template
from django.utils.html import mark_safe

register = template.Library()

# For including CSS/JS, so that we only have this code in one place.


@register.simple_tag
def include_d3_js(*args):
    "All the JS needed to use d3."
    return mark_safe("""
        <script src="https://d3js.org/d3.v3.min.js"></script>
    """)


@register.simple_tag
def include_maps_css(*args):
    "All the CSS needed to use Mapbox maps."
    return mark_safe("""
        <link rel="stylesheet" href="https://api.tiles.mapbox.com/mapbox.js/v2.1.2/mapbox.css" />
    """)


@register.simple_tag
def include_maps_js(*args, **kwargs):
    """"
    All the JS needed to use Mapbox maps.
    """
    return mark_safe("""
        <script src="https://api.tiles.mapbox.com/mapbox.js/v2.1.2/mapbox.js"></script>
    """)
