from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase

from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.letters.factories import LetterFactory
from pepysdiary.letters.models import Letter


class LetterManagerTestCase(TransactionTestCase):
    def test_get_brief_references(self):
        "It should return the correct data about topics referenced by Letter texts"

        topic_1 = TopicFactory(
            title="Cats",
            tooltip_text="About cats",
            thumbnail=SimpleUploadedFile(
                name="cat.jpg", content=b"", content_type="image/jpeg"
            ),
        )
        topic_2 = TopicFactory(title="Dogs", tooltip_text="About dogs")
        topic_3 = TopicFactory(title="Fish", tooltip_text="About fish")
        TopicFactory(title="Birds")

        letter_1 = LetterFactory(
            text=(
                "<p>"
                f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
                "</a> and "
                f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_3.id}/">fish'
                "</a>.</p>"
            )
        )
        letter_2 = LetterFactory(
            text=(
                "<p>"
                f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
                "</a> and "
                f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_2.id}/">dogs'
                "</a>.</p>"
            )
        )

        references = Letter.objects.get_brief_references([letter_1, letter_2])

        self.assertEqual(len(references.keys()), 3)
        self.assertEqual(
            references[str(topic_1.pk)],
            {
                "title": "Cats",
                "text": "About cats",
                "thumbnail_url": "/media/encyclopedia/thumbnails/cat.jpg",
            },
        )
        self.assertEqual(
            references[str(topic_3.pk)],
            {"title": "Fish", "text": "About fish", "thumbnail_url": ""},
        )
        self.assertEqual(
            references[str(topic_2.pk)],
            {"title": "Dogs", "text": "About dogs", "thumbnail_url": ""},
        )

        # Tidy up the file
        topic_1.thumbnail.delete()
