from rest_framework.renderers import JSONRenderer


class PrettyJSONRenderer(JSONRenderer):
    """
    Make the raw JSON responses more readable by indenting them.
    """

    def get_indent(self, accepted_media_type, renderer_context):
        return 2
