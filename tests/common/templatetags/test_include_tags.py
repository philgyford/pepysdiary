from django.test import TestCase

from pepysdiary.common.templatetags.include_tags import (
    include_d3_js,
    include_maps_css,
    include_maps_js,
)


class IncludeTagsTestCase(TestCase):
    def test_include_d3_js(self):
        self.assertEqual(
            include_d3_js(),
            """
        <script src="https://d3js.org/d3.v3.min.js"></script>
""",
        )

    def test_include_maps_css(self):
        # Need to take account of the cache-busting string added to end of filename.
        self.assertIn(
            '<link rel="stylesheet" href="/static/common/vendor/leaflet/leaflet_1.6.0.',
            include_maps_css(),
        )

    def test_include_maps_js(self):
        maps_js = include_maps_js()
        # Need to take account of the cache-busting string added to end of filenames.
        self.assertIn(
            '<script src="/static/common/vendor/leaflet/leaflet_1.6.0.', maps_js
        )
        self.assertIn(
            'js"></script><script src="/static/common/vendor/leaflet/leaflet-providers.',  # noqa: E501
            maps_js,
        )
