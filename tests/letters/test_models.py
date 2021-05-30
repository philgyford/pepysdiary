from django.test import TestCase

from django_comments.moderation import AlreadyModerated, moderator

from pepysdiary.common.utilities import make_date
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.letters.factories import LetterFactory
from pepysdiary.letters.models import Letter, LetterModerator


class LetterTestCase(TestCase):
    def test_str(self):
        letter = LetterFactory(title="My Letter", letter_date=make_date("1660-01-02"))
        self.assertEqual(str(letter), "1660-01-02: My Letter")

    def test_order(self):
        "It should be ordered by letter_date then order"
        letter_1 = LetterFactory(letter_date=make_date("1660-01-02"), order=1)
        letter_2 = LetterFactory(letter_date=make_date("1660-01-01"), order=2)
        letter_3 = LetterFactory(letter_date=make_date("1660-01-01"), order=1)
        letter_4 = LetterFactory(letter_date=make_date("1660-01-03"), order=1)

        letters = Letter.objects.all()

        self.assertEqual(letters[0], letter_3)
        self.assertEqual(letters[1], letter_2)
        self.assertEqual(letters[2], letter_1)
        self.assertEqual(letters[3], letter_4)

    def test_makes_references_on_save(self):
        "When a Letter is saved, any references should be updated."
        topic_1 = TopicFactory(title="Cats")
        topic_2 = TopicFactory(title="Dogs")
        topic_3 = TopicFactory(title="Fish")
        letter = LetterFactory(text="")

        # Manually add the letter as a reference only to topics 1 and 2:
        topic_1.letter_references.add(letter)
        topic_2.letter_references.add(letter)

        # Now save the letter with text referencing only topics 1 and 3:
        # This should update the references.
        letter.text = (
            "<p>Hello. "
            f'<a href="http://www.pepysdiary.com/encyclopedia/{topic_1.id}/">cats'
            "</a> and "
            f'<a href="https://www.pepysdiary.com/encyclopedia/{topic_3.id}/">fish'
            "</a>.</p>"
        )
        letter.save()

        # Should still be there:
        topic_1_refs = topic_1.letter_references.all()
        self.assertEqual(len(topic_1_refs), 1)
        self.assertEqual(topic_1_refs[0], letter)

        # Should no longer exist:
        topic_2_refs = topic_2.letter_references.all()
        self.assertEqual(len(topic_2_refs), 0)

        # Should have been added:
        topic_3_refs = topic_3.letter_references.all()
        self.assertEqual(len(topic_3_refs), 1)
        self.assertEqual(topic_3_refs[0], letter)

    def test_get_absolute_url(self):
        letter = LetterFactory(slug="my-letter", letter_date=make_date("1660-01-02"))
        self.assertEqual(letter.get_absolute_url(), "/letters/1660/01/02/my-letter/")

    def test_short_date(self):
        letter = LetterFactory(letter_date=make_date("1660-01-02"))
        self.assertEqual(letter.short_date, "2 Jan 1660")

    def test_full_title(self):
        letter = LetterFactory(title="My Letter", letter_date=make_date("1660-01-02"))
        self.assertEqual(letter.full_title, "2 Jan 1660, My Letter")

    # Testing PepysModel properties/methods:

    def test_short_title(self):
        "It should return the correct short title"
        letter = LetterFactory(title="My Letter")
        self.assertEqual(letter.short_title, letter.title)

    def test_get_a_comment_name(self):
        "It should retun the correct string"
        letter = LetterFactory()
        self.assertEqual(letter.get_a_comment_name(), "an annotation")

    # Testing OldDateMixin properties/methods:

    def test_old_dates(self):
        "The properties should return the correct data"
        letter = LetterFactory(letter_date=make_date("1660-01-02"))
        self.assertEqual(letter.year, "1660")
        self.assertEqual(letter.month, "01")
        self.assertEqual(letter.month_b, "Jan")
        self.assertEqual(letter.day, "02")
        self.assertEqual(letter.day_e, "2")


class LetterModeratorTestCase(TestCase):

    def test_it_is_registered(self):
        # Shouldn't be able to register it again:
        with self.assertRaises(AlreadyModerated):
            moderator.register(Letter, LetterModerator)
