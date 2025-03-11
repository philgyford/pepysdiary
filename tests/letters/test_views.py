from django.conf import settings
from django.http.response import Http404

from pepysdiary.common.utilities import make_date
from pepysdiary.encyclopedia.factories import PersonTopicFactory, TopicFactory
from pepysdiary.letters import views
from pepysdiary.letters.factories import LetterFactory
from tests import ViewTestCase, ViewTransactionTestCase


class LetterArchiveViewTestCase(ViewTestCase):
    def test_redirects(self):
        "It should redirect to the page for Pepys' letters"
        PersonTopicFactory(id=settings.PEPYS_TOPIC_ID)
        response = self.client.get("/letters/")
        self.assertRedirects(response, f"/letters/person/{settings.PEPYS_TOPIC_ID}/")


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
        "It 404s if there's no Letter"
        with self.assertRaises(Http404):
            views.LetterDetailView.as_view()(
                self.request, year="1661", month="01", day="02", slug="nope"
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
        self.assertEqual(response.template_name[0], "letters/letter_person.html")

    def test_response_404_no_topic(self):
        "If the person/topic doesn't exist, we 404"
        with self.assertRaises(Http404):
            views.LetterPersonView.as_view()(self.request, pk=123)

    def test_response_no_letters(self):
        "If there are no letters to/from a person who exists, we do not 404"
        person = PersonTopicFactory()
        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_context_data_letters(self):
        "The letters should be in the context data"
        person = PersonTopicFactory()
        letter_1 = LetterFactory(sender=person, letter_date=make_date("1670-01-01"))
        letter_2 = LetterFactory(recipient=person, letter_date=make_date("1666-01-01"))

        # Shouldn't be included:
        LetterFactory(sender=PersonTopicFactory())

        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("letter_list", response.context_data)
        self.assertQuerySetEqual(
            response.context_data["letter_list"], [letter_2, letter_1]
        )

    def test_context_data_person(self):
        "The topic should be included in the context data"
        person = PersonTopicFactory()
        LetterFactory(sender=person)

        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)

        self.assertEqual(response.context_data["person"], person)

    def test_context_data_letter_kind(self):
        person = PersonTopicFactory()
        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.context_data["letter_kind"], "both")

    def test_context_data_letter_counts(self):
        person = PersonTopicFactory()
        LetterFactory.create_batch(3, sender=person)
        LetterFactory.create_batch(2, recipient=person)

        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)

        self.assertDictEqual(
            response.context_data["letter_counts"], {"from": 3, "to": 2, "both": 5}
        )

    def test_context_correspondents(self):
        person1 = PersonTopicFactory()
        LetterFactory.create_batch(3, sender=person1)
        LetterFactory.create_batch(2, recipient=person1)
        person2 = PersonTopicFactory()
        LetterFactory.create_batch(1, sender=person2)
        LetterFactory.create_batch(5, recipient=person2)
        person3 = PersonTopicFactory()
        LetterFactory.create_batch(1, sender=person3)

        # Shouldn't be included:
        PersonTopicFactory()

        response = views.LetterPersonView.as_view()(self.request, pk=person1.pk)

        context = response.context_data
        self.assertEqual(len(context["correspondents"]), 3)
        self.assertEqual(context["correspondents"][0], person2)
        self.assertEqual(context["correspondents"][1], person1)
        self.assertEqual(context["correspondents"][2], person3)
        self.assertEqual(context["correspondents"][0].letter_count, 6)
        self.assertEqual(context["correspondents"][1].letter_count, 5)
        self.assertEqual(context["correspondents"][2].letter_count, 1)

    def test_ordering_default(self):
        "It should order letters by letter_date ascending by default"
        person = PersonTopicFactory()
        letter_1 = LetterFactory(sender=person, letter_date=make_date("1670-01-01"))
        letter_2 = LetterFactory(recipient=person, letter_date=make_date("1650-01-01"))
        letter_3 = LetterFactory(recipient=person, letter_date=make_date("1660-01-01"))

        response = views.LetterPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("letter_list", response.context_data)
        self.assertQuerySetEqual(
            response.context_data["letter_list"], [letter_2, letter_3, letter_1]
        )

    def test_ordering_date_created(self):
        "It should order letters by -date_created if ?o=added"
        person = PersonTopicFactory()
        letter_1 = LetterFactory(sender=person, letter_date=make_date("1670-01-01"))
        letter_2 = LetterFactory(recipient=person, letter_date=make_date("1650-01-01"))
        letter_3 = LetterFactory(recipient=person, letter_date=make_date("1660-01-01"))

        response = self.client.get(f"/letters/person/{person.pk}/?o=added")

        self.assertIn("letter_list", response.context_data)
        self.assertQuerySetEqual(
            response.context_data["letter_list"], [letter_3, letter_2, letter_1]
        )


class LetterFromPersonViewTestCase(ViewTransactionTestCase):
    def test_response_200(self):
        person = PersonTopicFactory()
        LetterFactory(sender=person)
        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        person = PersonTopicFactory()
        LetterFactory(sender=person)
        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.template_name[0], "letters/letter_person.html")

    def test_response_404_no_topic(self):
        "If the person/topic doesn't exist, we 404"
        with self.assertRaises(Http404):
            views.LetterFromPersonView.as_view()(self.request, pk=123)

    def test_response_no_letters(self):
        "If there are no letters from a person who exists, we do not 404"
        person = PersonTopicFactory()
        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_context_data_letters(self):
        "The letters should be in the context data"
        person = PersonTopicFactory()
        letter_1 = LetterFactory(sender=person, letter_date=make_date("1670-01-01"))
        letter_2 = LetterFactory(sender=person, letter_date=make_date("1666-01-01"))

        # Shouldn't be included:
        LetterFactory(recipient=person)
        LetterFactory(sender=PersonTopicFactory())

        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("letter_list", response.context_data)
        self.assertQuerySetEqual(
            response.context_data["letter_list"], [letter_2, letter_1]
        )

    def test_context_data_person(self):
        "The topic should be included in the context data"
        person = PersonTopicFactory()
        LetterFactory(sender=person)

        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)

        self.assertEqual(response.context_data["person"], person)

    def test_context_data_letter_kind(self):
        person = PersonTopicFactory()
        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.context_data["letter_kind"], "from")

    def test_context_data_letter_counts(self):
        person = PersonTopicFactory()
        LetterFactory.create_batch(3, sender=person)
        LetterFactory.create_batch(2, recipient=person)

        response = views.LetterFromPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("person", response.context_data)
        self.assertDictEqual(
            response.context_data["letter_counts"], {"from": 3, "to": 2, "both": 5}
        )


class LetterToPersonViewTestCase(ViewTransactionTestCase):
    def test_response_200(self):
        person = PersonTopicFactory()
        LetterFactory(recipient=person)
        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        person = PersonTopicFactory()
        LetterFactory(recipient=person)
        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.template_name[0], "letters/letter_person.html")

    def test_response_404_no_topic(self):
        "If the person/topic doesn't exist, we 404"
        with self.assertRaises(Http404):
            views.LetterToPersonView.as_view()(self.request, pk=123)

    def test_response_no_letters(self):
        "If there are no letters to a person who exists, we do not 404"
        person = PersonTopicFactory()
        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_context_data_letters(self):
        "The letters should be in the context data"
        person = PersonTopicFactory()
        letter_1 = LetterFactory(recipient=person, letter_date=make_date("1670-01-01"))
        letter_2 = LetterFactory(recipient=person, letter_date=make_date("1666-01-01"))

        # Shouldn't be included:
        LetterFactory(sender=person)
        LetterFactory(sender=PersonTopicFactory())

        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("letter_list", response.context_data)
        self.assertQuerySetEqual(
            response.context_data["letter_list"], [letter_2, letter_1]
        )

    def test_context_data_person(self):
        "The topic should be included in the context data"
        person = PersonTopicFactory()
        LetterFactory(recipient=person)

        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)

        self.assertEqual(response.context_data["person"], person)

    def test_context_data_letter_kind(self):
        person = PersonTopicFactory()
        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.context_data["letter_kind"], "to")

    def test_context_data_letter_counts(self):
        person = PersonTopicFactory()
        LetterFactory.create_batch(3, sender=person)
        LetterFactory.create_batch(2, recipient=person)

        response = views.LetterToPersonView.as_view()(self.request, pk=person.pk)

        self.assertIn("person", response.context_data)
        self.assertDictEqual(
            response.context_data["letter_counts"], {"from": 3, "to": 2, "both": 5}
        )
