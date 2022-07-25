from django.conf import settings
from django.test import TestCase, override_settings

from pepysdiary.annotations.forms import AnnotationForm
from pepysdiary.annotations.models import Annotation
from pepysdiary.diary.factories import EntryFactory


class AnnotationFormTestCase(TestCase):
    """Testing the AnnotationForm works as expected.
    Yes, we're not *only* testing that class because we're submitting
    the comment by posting to a view, but seems a simple way to ensure
    it's all working as expected.
    """

    @override_settings()
    def test_clean_comment_blank_lines(self):
        "It should replace three or more blank lines with two."
        del settings.PEPYS_AKISMET_API_KEY

        entry = EntryFactory()
        form = AnnotationForm(entry)

        data = {
            "name": "Bob",
            "email": "bob@example.org",
            "url": "",
            "comment": """Hello.




  This is untouched.

Bye.""",
        }
        data.update(form.initial)

        self.client.post("/annotations/post/", data, REMOTE_ADDR="1.2.3.4")

        annotation = Annotation.objects.first()
        self.assertEqual(
            annotation.comment,
            """Hello.

  This is untouched.

Bye.""",
        )

    @override_settings()
    def test_clean_comment_strip_spaces(self):
        "It should strip leading and trailing spaces."
        del settings.PEPYS_AKISMET_API_KEY

        entry = EntryFactory()
        form = AnnotationForm(entry)

        data = {
            "name": "Bob",
            "email": "bob@example.org",
            "url": "",
            "comment": "   Hello.   ",
        }
        data.update(form.initial)

        self.client.post("/annotations/post/", data, REMOTE_ADDR="1.2.3.4")

        annotation = Annotation.objects.first()
        self.assertEqual(annotation.comment, "Hello.")
