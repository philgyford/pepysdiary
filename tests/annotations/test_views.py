from django.core import mail
from django.test import override_settings, TestCase
from django.urls import reverse
from django.utils.http import urlencode

from pepysdiary.annotations.factories import EntryAnnotationFactory
from pepysdiary.membership.factories import PersonFactory


class FlagTestCase(TestCase):
    def setUp(self):
        self.annotation = EntryAnnotationFactory()
        self.url = reverse(
            "annotations-flag", kwargs={"comment_id": self.annotation.pk}
        )

    def log_user_in(self):
        """Log the user in to self.client.
        Use before a request to self.client to perform that request logged in.
        The created user is returned.
        """
        user = PersonFactory()
        self.client.force_login(user)
        return user

    def test_get_200(self):
        self.log_user_in()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_404(self):
        "It should 404 if the comment doesn't exist"
        self.log_user_in()
        url = reverse("annotations-flag", kwargs={"comment_id": self.annotation.pk + 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_template(self):
        self.log_user_in()
        response = self.client.get(self.url)
        self.assertEqual(response.templates[0].name, "comments/flag.html")

    def test_get_context(self):
        "The comment should be supplied to the template"
        self.log_user_in()
        response = self.client.get(self.url)
        self.assertEqual(response.context["comment"], self.annotation)
        self.assertEqual(response.context["next"], None)

    def test_login_required(self):
        "It should redirect to login if the user isn't logged in"
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse("login") + "?" + urlencode({"next": self.url})
        )

    def test_post_404(self):
        "It should 404 if the comment doesn't exist"
        self.log_user_in()
        url = reverse("annotations-flag", kwargs={"comment_id": self.annotation.pk + 1})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    @override_settings(COMMENT_FLAG_EMAIL="bob@example.org")
    def test_post_sends_email(self):
        """It should send an email to the correct email address.
        Because our custom method doesn't create a CommentFlag, it sends an email.
        """
        self.log_user_in()
        self.client.post(self.url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Pepys' Diary Flag")
        self.assertEqual(mail.outbox[0].to, ["bob@example.org"])

    def test_post_redirects_to_default_url(self):
        "If no next parameter is passed in, it redirects to comments-flag-done"
        self.log_user_in()
        response = self.client.post(self.url)
        redirect_url = (
            reverse("comments-flag-done") + "?" + urlencode({"c": self.annotation.pk})
        )
        self.assertRedirects(response, redirect_url)

    def test_post_redirects_to_next(self):
        "If a next parameter is passed in, it redirects to that URL"
        self.log_user_in()
        response = self.client.post(self.url, {"next": reverse("home")})
        redirect_url = reverse("home") + "?" + urlencode({"c": self.annotation.pk})
        self.assertRedirects(response, redirect_url)
