from django.test import TestCase

from pepysdiary.annotations.factories import EntryAnnotationFactory
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.membership.factories import PersonFactory


class CommentTemplateTest(TestCase):
    def setUp(self):
        self.user = PersonFactory()
        self.entry = EntryFactory()
        self.annotation = EntryAnnotationFactory(
            content_object=self.entry, user=self.user
        )

    def test_profile_link_enabled_when_user_active(self):
        formatted_date = self.entry.diary_date.strftime("%Y/%m/%d")
        expected_link = (
            f'<a href="/account/profile/{self.user.id}/" '
            f'title="See more about this person">{self.user.name}</a>'
        )
        response = self.client.get(f"/diary/{formatted_date}/")

        self.assertContains(response, "1 Annotation", html=True)
        self.assertContains(response, expected_link, html=True)

    def test_profile_link_disabled_when_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        formatted_date = self.entry.diary_date.strftime("%Y/%m/%d")
        expected_link = (
            f'<a href="/account/profile/{self.user.id}/" '
            f'title="See more about this person">{self.user.name}</a>'
        )
        response = self.client.get(f"/diary/{formatted_date}/")

        self.assertContains(response, "1 Annotation", html=True)
        self.assertNotContains(response, expected_link, html=True)
