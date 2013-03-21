from django import template

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
        <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.5.1/leaflet.css" />
        <!--[if lte IE 8]>
            <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.5.1/leaflet.ie.css" />
        <![endif]-->
    """


@register.simple_tag
def include_leaflet_js(*args):
    "All the JS needed to use Leaflet maps."
    return """
        <script src="http://cdn.leafletjs.com/leaflet-0.5.1/leaflet.js"></script>
    """
