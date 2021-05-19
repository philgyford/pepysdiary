from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase

from pepysdiary.common.models import OldDateMixin, PepysModel


class TitleModel(PepysModel):
    "Used to check behaviuor of a child class with a title attribute"

    title = models.CharField(max_length=255)

    class Meta:
        app_label = "pepydiary.diary"


class NoTitleModel(PepysModel):
    "Used to check behaviuor of a child class with NO title attribute"

    class Meta:
        app_label = "pepydiary.diary"


class NoOldDateFieldModel(OldDateMixin):
    "Used to check behaviuor of a class that doesn't set old_date_field"

    class Meta:
        app_label = "pepydiary.diary"


class PepysModelTestCase(TestCase):
    """Most behaviour is tested in tests for child classes.
    But we can't test the absence of a title attribute in those, so...
    """

    def test_model_with_title(self):
        obj = TitleModel(title="Foo")
        self.assertEqual(obj.short_title, "Foo")

    def test_model_without_title(self):
        obj = NoTitleModel()
        self.assertEqual(obj.short_title, "")


class OldDateMixinTestCase(TestCase):
    """Most behaviour is tested in tests for child classes.
    But we can't test old_date_field not being set in those, so...
    """

    def test_error_with_no_old_date_field(self):
        obj = NoOldDateFieldModel()
        with self.assertRaises(ImproperlyConfigured):
            obj.get_old_date()
