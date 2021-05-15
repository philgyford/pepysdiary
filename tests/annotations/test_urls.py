from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.annotations import views
from pepysdiary.annotations.factories import EntryAnnotationFactory


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class AnnotationsURLsTestCase(TestCase):
    def test_annotations_flag_url(self):
        annotation = EntryAnnotationFactory()
        self.assertEqual(
            reverse("annotations-flag", kwargs={"comment_id": annotation.pk}),
            f"/annotations/flagging/flag/{annotation.pk}/",
        )

    def test_annotations_flag_view(self):
        annotation = EntryAnnotationFactory()
        self.assertEqual(
            resolve(f"/annotations/flagging/flag/{annotation.pk}/").func, views.flag
        )
