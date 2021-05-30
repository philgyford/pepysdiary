from django.http.response import Http404
from django.test import override_settings

from pepysdiary.common.utilities import make_date
from pepysdiary.letters import views
from pepysdiary.letters.factories import LetterFactory
from pepysdiary.encyclopedia.factories import PersonTopicFactory, TopicFactory
from tests import ViewTestCase, ViewTransactionTestCase


class LetterDetailViewTestCase(ViewTestCase):
    def test_response_200(self):
        LetterFactory(letter_date=make_date("1661-01-02"), slug="my-letter")
        response = views.LetterDetailView.as_view()(
            self.request, year="1661", month="01", day="02", slug="my-letter"
        )
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        LetterFactory(letter_date=make_date("1661-01-02"), slug="my-letter")
        response = views.LetterDetailView.as_view()(
            self.request, year="1661", month="01", day="02", slug="my-letter"
        )
        self.assertEqual(response.template_name[0], "letters/letter_detail.html")

    def test_response_404_no_letter(self):
        "It 404s if there's no Lette "
        with self.assertRaises(Http404):
            views.LetterDetailView.as_view()(
                self.request, year="1661", month="01", day="02", slug="my-letter"
            )

    def test_context_data_letter(self):
        "The letter should be sent to the template"
        letter = LetterFactory(letter_date=make_date("1661-01-02"), slug="my-letter")

        response = views.LetterDetailView.as_view()(
            self.request, year="1661", month="01", day="02", slug="my-letter"
        )

        data = response.context_data
        self.assertIn("object", data)
        self.assertIn("letter", data)
        self.assertEqual(data["letter"], data["object"])
        self.assertEqual(data["letter"], letter)

    def test_context_data_tooltip_references(self):
        "The tooltip_references are sent to the template"
        letter = LetterFactory(letter_date=make_date("1661-01-02"), slug="my-letter")
        topic_1 = TopicFactory(title="Cats", tooltip_text="About cats")
        topic_2 = TopicFactory(title="Dogs", tooltip_text="About dogs")
        topic_1.letter_references.add(letter)
        topic_2.letter_references.add(letter)

        response = views.LetterDetailView.as_view()(
            self.request, year="1661", month="01", day="02", slug="my-letter"
        )

        self.assertIn("tooltip_references", response.context_data)
        self.assertEqual(
            response.context_data["tooltip_references"],
            {
                str(topic_1.pk): {
                    "title": "Cats",
                    "text": "About cats",
                    "thumbnail_url": "",
                },
                str(topic_2.pk): {
                    "title": "Dogs",
                    "text": "About dogs",
                    "thumbnail_url": "",
                },
            },
        )

    def test_context_data_next_previous(self):
        "The next/previous Letters should be sent to the template if they exist"
        prev_letter = LetterFactory(letter_date=make_date("1661-01-02"), order=1)
        LetterFactory(letter_date=make_date("1661-01-02"), order=2, slug="my-letter")
        next_letter = LetterFactory(letter_date=make_date("1661-01-03"), order=1)

        response = views.LetterDetailView.as_view()(
            self.request, year="1661", month="01", day="02", slug="my-letter"
        )

        data = response.context_data
        self.assertIn("previous_letter", data)
        self.assertEqual(data["previous_letter"], prev_letter)
        self.assertIn("next_letter", data)
        self.assertEqual(data["next_letter"], next_letter)

    def test_context_data_no_next_previous(self):
        "If there's no next/previous letters, None is sent to the template"
        LetterFactory(letter_date=make_date("1661-01-02"), order=2, slug="my-letter")

        response = views.LetterDetailView.as_view()(
            self.request, year="1661", month="01", day="02", slug="my-letter"
        )

        data = response.context_data
        self.assertIn("previous_letter", data)
        self.assertIsNone(data["previous_letter"])
        self.assertIn("next_letter", data)
        self.assertIsNone(data["next_letter"])


class LetterPersonViewTestCase(ViewTransactionTestCase):
    def test_response_200(self):
        person = PersonTopicFactory()
        LetterFactory(sender=person)
        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        person = PersonTopicFactory()
        LetterFactory(sender=person)
        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.template_name[0], "letter_person.html")

    def test_response_404_no_topic(self):
        "If the person/topic doesn't exist, we 404"
        with self.assertRaises(Http404):
            views.LetterPersonView.as_view()(self.request, pk=123)

    def test_response_404_no_letters(self):
        "If there are no letters to/from a person who exists, we 404"
        person = PersonTopicFactory()
        with self.assertRaises(Http404):
            views.LetterPersonView.as_view()(self.request, pk=person.pk)

    @override_settings(PEPYS_TOPIC_ID=123)
    def test_redirects_for_samuel_pepys(self):
        "Pepys' Topic is a special case - we should redirect to the fron Letters page"
        person = PersonTopicFactory(pk=123)
        LetterFactory(sender=person)
        response = self.client.get(f"/letters/person/{person.pk}/")
        self.assertRedirects(response, "/letters/")

    def test_context_data_letters(self):
        "The letters should be in the context data"
        person = PersonTopicFactory()
        letter_1 = LetterFactory(sender=person)
        letter_2 = LetterFactory(recipient=person)

        # Shouldn't be included:
        LetterFactory(sender=PersonTopicFactory())

        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)

        data = response.context_data
        self.assertIn("object_list", data)
        self.assertIn("letter_list", data)
        self.assertEqual(data["object_list"], data["letter_list"])
        self.assertEqual(len(data["letter_list"]), 2)
        self.assertIn(letter_1, data["letter_list"])
        self.assertIn(letter_2, data["letter_list"])

    def test_context_data_person(self):
        "The topic should be included in the context data"
        person = PersonTopicFactory()
        LetterFactory(sender=person)

        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("person", response.context_data)
        self.assertEqual(response.context_data["person"], person)


class LetterArchiveViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.LetterArchiveView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.LetterArchiveView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "letter_list.html")

    def test_context_data_letters(self):
        "The letters should be in the context data"
        LetterFactory()
        LetterFactory()

        response = views.LetterArchiveView.as_view()(self.request)

        data = response.context_data
        self.assertIn("letters", data)
        self.assertEqual(len(data["letters"]), 2)
