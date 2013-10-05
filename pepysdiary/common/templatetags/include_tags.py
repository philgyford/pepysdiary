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
def include_leaflet_css(*args):
    "All the CSS needed to use Leaflet maps."
    return """
        <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.css" />
        <!--[if lte IE 8]>
            <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.ie.css" />
        <![endif]-->
    """


@register.simple_tag
def include_leaflet_js(*args, **kwargs):
    """"
    All the JS needed to use Leaflet maps.
    kwargs can have:
        `include_labels` to include the code for hover labels.
    """
    html = """
        <script src="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.js"></script>
    """
    if kwargs.get('include_labels', False) is True:
        html += """
            <script src="%sjs/libs/leaflet.label.min.js"></script>
        """ % settings.STATIC_URL
    return html
