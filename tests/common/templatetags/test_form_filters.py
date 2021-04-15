from types import SimpleNamespace

from django import forms
from django.test import TestCase

from pepysdiary.common.templatetags.form_filters import tabindex


class TabIndexTestCase(TestCase):

    def test_tabindex(self):
        # Make a fake value like what would be passed from the template:
        value = SimpleNamespace()
        value.field = forms.CharField()

        value = tabindex(value, 3)

        self.assertIn("tabindex", value.field.widget.attrs)
        self.assertEqual(value.field.widget.attrs["tabindex"], 3)
