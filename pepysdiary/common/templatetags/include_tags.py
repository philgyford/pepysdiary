from django import template
from django.conf import settings

register = template.Library()

# For including CSS/JS, so that we only have this code in one place.


@register.simple_tag
def include_d3_js(*args):
    "All the JS needed to use d3."
    return """
        <script src="http://d3js.org/d3.v3.min.js"></script>
    """


@register.simple_tag
def include_maps_css(*args):
    "All the CSS needed to use Mapbox maps."
    return """
        <link rel="stylesheet" href="https://api.tiles.mapbox.com/mapbox.js/v1.6.2/mapbox.css" />
    """


@register.simple_tag
def include_maps_js(*args, **kwargs):
    """"
    All the JS needed to use Mapbox maps.
    kwargs can have:
        `include_labels` to include the code for hover labels.
    """
    html = """
        <script src="https://api.tiles.mapbox.com/mapbox.js/v1.6.2/mapbox.js"></script>
    """
    if kwargs.get('include_labels', False) is True:
        html += """
            <script src="%sjs/libs/leaflet.label.min.js"></script>
        """ % settings.STATIC_URL
    return html
