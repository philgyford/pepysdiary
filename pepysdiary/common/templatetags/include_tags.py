from django import template
from django.templatetags.static import static
from django.utils.html import mark_safe

register = template.Library()

# For including CSS/JS, so that we only have this code in one place.


@register.simple_tag
def include_d3_js(*args):
    "All the JS needed to use d3."
    return mark_safe(
        """
        <script src="https://d3js.org/d3.v3.min.js"></script>
    """
    )


@register.simple_tag
def include_maps_css(*args):
    "All the CSS needed to use Leaflet maps."
    css_url = static("common/vendor/leaflet/leaflet_1.6.0.css")
    return mark_safe(f'<link rel="stylesheet" href="{css_url}">')


@register.simple_tag
def include_maps_js(*args, **kwargs):
    """"
    All the JS needed to use Leaflet maps.
    """
    leaflet_url = static("common/vendor/leaflet/leaflet_1.6.0.js")
    providers_url = static("common/vendor/leaflet/leaflet-providers.js")
    return mark_safe(
        f'<script src="{leaflet_url}"></script>'
        f'<script src="{providers_url}"></script>'
    )
