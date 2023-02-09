# from unittest.mock import patch

# from captcha.client import RecaptchaResponse
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.contrib.sites.models import Site
from django.core import mail
from django.http.response import Http404
from django.test import TestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from freezegun import freeze_time

from pepysdiary.annotations.factories import PostAnnotationFactory
from pepysdiary.common.factories import ConfigFactory
from pepysdiary.common.utilities import make_datetime
from pepysdiary.membership import views
from pepysdiary.membership.factories import PersonFactory
from pepysdiary.membership.models import Person
from tests import ViewTestCase


def make_password_reset_url(user):
    """
    Generate a URL to passsword_reset_confirm for a specific user.

    Copied from django.contrib.auth.forms.PasswordResetForm
    https://github.com/django/django/blob/main/django/contrib/auth/forms.py#L241
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    return f"/account/reset/{uid}/{token}/"


def make_password_reset_form_url(user):
    """Generate the URL for the reset password form.
    This is the URL the user gets redirected to after they click the
    make_password_reset_url() URL in an email.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return f"/account/reset/{uid}/set-password/"


class LoginTestCase(TestCase):
    "Parent so we don't need to repeat this method."

    def log_user_in(self):
        """Log the user in to self.client.
        Use before a request to self.client to perform that request logged in.
        The created user is returned.
        """
        user = PersonFactory()
        self.client.force_login(user)
        return user


class ActivateViewTestCase(TestCase):
    def test_registration_not_allowed(self):
        ConfigFactory(allow_registration=False)

        response = self.client.get("/account/activate/123456abcdef/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], "membership/message.html")
        self.assertIn(
            "Sorry, registration isn’t allowed at the moment.",
            response.content.decode(),
        )

    @freeze_time("2021-01-01 12:00:00", tz_offset=0)
    def test_registration_success(self):
        "If there's a matching user, they should be activated, and we redirect"
        key = "1234567890123456789012345678901234567890"
        ConfigFactory(allow_registration=True)
        person = PersonFactory(is_active=False, activation_key=key, date_activated=None)

        response = self.client.get(f"/account/activate/{key}/")
        person.refresh_from_db()

        self.assertRedirects(response, "/account/activate/complete/")
        self.assertTrue(person.is_active)
        self.assertEqual(person.activation_key, Person.ACTIVATED)
        self.assertEqual(person.date_activated, make_datetime("2021-01-01 12:00:00"))

    def test_registration_fails(self):
        "If the key doesn't match a user, it fails."
        ConfigFactory(allow_registration=True)
        person = PersonFactory(
            is_active=False,
            activation_key="1234567890123456789012345678901234567890",
            date_activated=None,
        )

        # Still using an activation key of the correct length.
        response = self.client.get(
            "/account/activate/abcdefghijabcdefghijabcdefghijabcdefghij/"
        )
        person.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], "membership/message.html")
        self.assertFalse(person.is_active)


class ActivateCompleteView(LoginTestCase):
    def test_response_200(self):
        response = self.client.get("/account/activate/complete/")
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get("/account/activate/complete/")
        self.assertEqual(response.template_name[0], "membership/message.html")

    def test_redirects_if_user_is_logged_in(self):
        self.log_user_in()
        response = self.client.get("/account/activate/complete/")
        self.assertRedirects(response, "/")


class EditProfileViewTestCase(LoginTestCase):
    def test_response_200(self):
        "Logged in user should be able to access it"
        self.log_user_in()
        response = self.client.get("/account/edit/")
        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_user(self):
        "A user who isn't logged in should be redirected to login page"
        response = self.client.get("/account/edit/")
        self.assertRedirects(response, "/account/login/?next=/account/edit/")

    def test_template(self):
        self.log_user_in()
        response = self.client.get("/account/edit/")
        self.assertEqual(response.template_name[0], "membership/person_form.html")

    def test_form_success(self):
        person = self.log_user_in()
        person.email = "bob@example.com"
        person.url = "https://example.com"
        person.save()

        data = {"email": "terry@example.org", "url": "https://example.org"}
        response = self.client.post("/account/edit/", data)

        person = Person.objects.first()
        self.assertRedirects(response, "/account/profile/")
        self.assertEqual(person.email, "terry@example.org")
        self.assertEqual(person.url, "https://example.org")

    def test_form_email_is_required(self):
        "If email is empty, same page should be returned, nothing should be updated"
        person = self.log_user_in()
        person.email = "bob@example.com"
        person.url = "https://example.com"
        person.save()

        data = {"email": "", "url": "https://example.com"}
        response = self.client.post("/account/edit/", data)

        person = Person.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(person.email, "bob@example.com")
        self.assertEqual(person.url, "https://example.com")

    def test_form_url_is_not_required(self):
        "If URL is empty, user should be udpated"
        person = self.log_user_in()
        person.email = "bob@example.com"
        person.url = "https://example.com"
        person.save()

        data = {"email": "bob@example.com", "url": ""}
        response = self.client.post("/account/edit/", data)

        person = Person.objects.first()
        self.assertRedirects(response, "/account/profile/")
        self.assertEqual(person.email, "bob@example.com")
        self.assertEqual(person.url, None)

    def test_name_cannot_be_changed(self):
        "The user's name cannot be changed"
        person = self.log_user_in()
        person.name = "Bob"
        person.email = "bob@example.com"
        person.save()

        data = {"name": "Terry", "email": "bob@example.com", "url": ""}
        response = self.client.post("/account/edit/", data)

        person = Person.objects.first()
        self.assertRedirects(response, "/account/profile/")
        self.assertEqual(person.name, "Bob")

    def test_email_must_not_already_exist(self):
        "The user can't change their email to one used by someone else"
        person = self.log_user_in()
        person.email = "bob@example.com"
        person.save()

        # A different user:
        PersonFactory(email="terry@example.org")

        data = {"email": "terry@example.org", "url": ""}
        response = self.client.post("/account/edit/", data)

        person.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        # Still the same as before:
        self.assertEqual(person.email, "bob@example.com")


class LoginViewTestCase(LoginTestCase):
    def test_response_200(self):
        response = self.client.get("/account/login/")
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get("/account/login/")
        self.assertEqual(response.template_name[0], "membership/login.html")

    def test_redirects_if_user_is_logged_in(self):
        self.log_user_in()
        response = self.client.get("/account/login/")
        self.assertRedirects(response, "/")

    def test_successful_login(self):
        "It should redirect, show a message, and log the user in."
        ConfigFactory(allow_login=True)
        PersonFactory(
            name="Bob",
            email="bob@example.org",
            password=make_password("my-password-123"),
        )

        data = {"username": "bob@example.org", "password": "my-password-123"}
        response = self.client.post("/account/login/", data)

        self.assertRedirects(response, "/")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You’re now logged in as Bob.")

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_unsuccessful_login(self):
        "It should stay on the same page and have an error message"
        data = {"username": "bob@example.org", "password": "my-password-123"}
        response = self.client.post("/account/login/", data)

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].errors.as_data()
        self.assertIn(
            "Please enter a correct Email address and password.",
            str(errors["__all__"][0]),
        )

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_should_not_work_if_disabled_in_config(self):
        ConfigFactory(allow_login=False)
        PersonFactory(
            email="bob@example.org", password=make_password("my-password-123")
        )

        # Valid data
        data = {"username": "bob@example.org", "password": "my-password-123"}
        response = self.client.post("/account/login/", data)

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].errors.as_data()
        self.assertEqual(
            "Sorry, logging in is currently disabled.",
            str(errors["__all__"][0].message),
        )

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class LogoutViewTestCase(LoginTestCase):
    def test_response_200(self):
        response = self.client.get("/account/logout/")
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get("/account/logout/")
        self.assertEqual(response.template_name[0], "membership/message.html")

    def test_logs_user_out(self):
        "It should log the user out."
        self.log_user_in()

        response = self.client.get("/account/logout/")

        self.assertEqual(response.status_code, 200)

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class MessageViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.MessageView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.MessageView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "membership/message.html")


class PasswordResetViewTestCase(TestCase):
    def test_response_200(self):
        response = self.client.get("/account/password/reset/")
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get("/account/password/reset/")
        self.assertEqual(response.template_name[0], "membership/password_reset.html")

    def test_form_success(self):
        "It should redirect and an email should be sent to the email address"
        site = Site.objects.first()
        site.domain = "example.com"
        site.name = "The Diary of Samuel Pepys"
        site.save()
        person = PersonFactory(email="bob@example.org")

        response = self.client.post(
            "/account/password/reset/", {"email": "bob@example.org"}
        )

        self.assertRedirects(response, "/account/password/reset/done/")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], "bob@example.org")
        self.assertEqual(
            mail.outbox[0].subject, "Password reset on The Diary of Samuel Pepys"
        )

        reset_url = "http://example.com" + make_password_reset_url(person)
        self.assertIn(reset_url, mail.outbox[0].body)

    def test_form_email_does_not_exist(self):
        "If the email address doesn't exit, it should redirect but not send an email"

        response = self.client.post(
            "/account/password/reset/", {"email": "bob@example.org"}
        )

        self.assertRedirects(response, "/account/password/reset/done/")

        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_address(self):
        "If an invalid email address is entered, the page is shown again."
        response = self.client.post("/account/password/reset/", {"email": "bob"})
        self.assertEqual(response.status_code, 200)
        # And no email is sent.
        self.assertEqual(len(mail.outbox), 0)


class PassworResetDoneViewTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.PasswordResetDoneView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.PasswordResetDoneView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "membership/message.html")


class PasswordResetConfirmViewTestCase(TestCase):
    def test_email_url_response_redirects(self):
        "If the email URL is correct, we redirect to the actual password form page"
        person = PersonFactory()
        response = self.client.get(make_password_reset_url(person))
        self.assertRedirects(response, make_password_reset_form_url(person))

    def test_response_200(self):
        "On the actual password form page, should get a 200"
        person = PersonFactory()
        response = self.client.get(make_password_reset_form_url(person))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        "On the actual password form page, we should use the correct template"
        person = PersonFactory()
        response = self.client.get(make_password_reset_form_url(person))
        self.assertEqual(response.template_name[0], "membership/password_confirm.html")


class PasswordResetCompleteTestCase(ViewTestCase):
    def test_response_200(self):
        response = views.PasswordResetCompleteView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = views.PasswordResetCompleteView.as_view()(self.request)
        self.assertEqual(response.template_name[0], "membership/message.html")


class PrivateProfileViewTestCase(LoginTestCase):
    "The private view of a profile"

    def test_response_200(self):
        "Logged in user should be able to access it"
        self.log_user_in()
        response = self.client.get("/account/profile/")
        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_user(self):
        "A user who isn't logged in should be redirected to login page"
        response = self.client.get("/account/profile/")
        self.assertRedirects(response, "/account/login/?next=/account/profile/")

    def test_template(self):
        self.log_user_in()
        response = self.client.get("/account/profile/")
        self.assertEqual(response.template_name[0], "membership/person_detail.html")

    def test_context_data_basics(self):
        "Context data should indicate private/public and contain the person"
        person = self.log_user_in()
        response = self.client.get("/account/profile/")

        data = response.context_data
        self.assertIn("is_private_profile", data)
        self.assertTrue(data["is_private_profile"])
        self.assertEqual(data["object"], person)

    def test_context_data_annotations_pagination(self):
        "Context data should contain 20 of the person's annotations"
        person = self.log_user_in()
        PostAnnotationFactory.create_batch(21, user=person)

        response = self.client.get("/account/profile/")

        data = response.context_data
        self.assertIn("comment_list", data)
        self.assertEqual(len(data["comment_list"]), 20)

    def test_context_data_annotations_content(self):
        "Context data should only contain this user's visible annotations"
        person = self.log_user_in()
        annotation = PostAnnotationFactory(
            user=person, is_public=True, is_removed=False
        )
        # Should not appear:
        PostAnnotationFactory(user=person, is_public=False, is_removed=False)
        PostAnnotationFactory(user=person, is_public=True, is_removed=True)
        PostAnnotationFactory(is_public=True, is_removed=False)

        response = self.client.get("/account/profile/")

        data = response.context_data
        self.assertEqual(len(data["comment_list"]), 1)
        self.assertIn(annotation, data["comment_list"])

    def test_context_data_annotations_ordering(self):
        "Annotations should be in reverse order of submission"
        person = self.log_user_in()
        annotation_1 = PostAnnotationFactory(
            user=person, submit_date=make_datetime("2021-01-02 12:00:00")
        )
        annotation_2 = PostAnnotationFactory(
            user=person, submit_date=make_datetime("2021-01-01 12:00:00")
        )
        annotation_3 = PostAnnotationFactory(
            user=person, submit_date=make_datetime("2021-01-03 12:00:00")
        )

        response = self.client.get("/account/profile/")

        data = response.context_data
        self.assertEqual(data["comment_list"][0], annotation_3)
        self.assertEqual(data["comment_list"][1], annotation_1)
        self.assertEqual(data["comment_list"][2], annotation_2)


class ProfileViewTestCase(ViewTestCase):
    "The public view of a profile"

    def test_response_200(self):
        person = PersonFactory(is_active=True)
        response = views.ProfileView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.status_code, 200)

    def test_response_404_if_person_does_not_exist(self):
        with self.assertRaises(Http404):
            views.ProfileView.as_view()(self.request, pk=1)

    def test_response_404_if_person_is_not_active(self):
        person = PersonFactory(is_active=False)
        with self.assertRaises(Http404):
            views.ProfileView.as_view()(self.request, pk=person.pk)

    def test_template(self):
        person = PersonFactory()
        response = views.ProfileView.as_view()(self.request, pk=person.pk)
        self.assertEqual(response.template_name[0], "membership/person_detail.html")

    def test_context_data_basics(self):
        "Context data should indicate private/public and contain the person"
        person = PersonFactory()
        response = views.ProfileView.as_view()(self.request, pk=person.pk)

        data = response.context_data
        self.assertIn("is_private_profile", data)
        self.assertFalse(data["is_private_profile"])
        self.assertEqual(data["object"], person)

    def test_context_data_annotations_pagination(self):
        "Context data should contain 20 of the person's annotations"
        person = PersonFactory()
        PostAnnotationFactory.create_batch(21, user=person)

        response = views.ProfileView.as_view()(self.request, pk=person.pk)

        data = response.context_data
        self.assertIn("comment_list", data)
        self.assertEqual(len(data["comment_list"]), 20)

    def test_context_data_annotations_content(self):
        "Context data should only contain this user's visible annotations"
        person = PersonFactory()
        annotation = PostAnnotationFactory(
            user=person, is_public=True, is_removed=False
        )
        # Should not appear:
        PostAnnotationFactory(user=person, is_public=False, is_removed=False)
        PostAnnotationFactory(user=person, is_public=True, is_removed=True)
        PostAnnotationFactory(is_public=True, is_removed=False)

        response = views.ProfileView.as_view()(self.request, pk=person.pk)

        data = response.context_data
        self.assertEqual(len(data["comment_list"]), 1)
        self.assertIn(annotation, data["comment_list"])

    def test_context_data_annotations_ordering(self):
        "Annotations should be in reverse order of submission"
        person = PersonFactory()
        annotation_1 = PostAnnotationFactory(
            user=person, submit_date=make_datetime("2021-01-02 12:00:00")
        )
        annotation_2 = PostAnnotationFactory(
            user=person, submit_date=make_datetime("2021-01-01 12:00:00")
        )
        annotation_3 = PostAnnotationFactory(
            user=person, submit_date=make_datetime("2021-01-03 12:00:00")
        )

        response = views.ProfileView.as_view()(self.request, pk=person.pk)

        data = response.context_data
        self.assertEqual(data["comment_list"][0], annotation_3)
        self.assertEqual(data["comment_list"][1], annotation_1)
        self.assertEqual(data["comment_list"][2], annotation_2)


class RegisterViewTestCase(LoginTestCase):
    "Also testing their associated Forms"

    def test_response_200(self):
        response = self.client.get("/account/register/")
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get("/account/register/")
        self.assertEqual(response.template_name[0], "membership/register.html")

    def test_redirects_if_user_is_logged_in(self):
        self.log_user_in()
        response = self.client.get("/account/register/")
        self.assertRedirects(response, "/")

    def test_successful_form_submission(self):
        "It should create a new inactive user, and redirect to complete page"
        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "https://example.com",
            "honeypot": "",
        }
        response = self.client.post("/account/register/", data)

        person = Person.objects.first()
        self.assertRedirects(response, "/account/register/complete/")
        self.assertEqual(person.name, "Bob")
        self.assertEqual(person.email, "bob@example.com")
        self.assertEqual(person.url, "https://example.com")
        self.assertFalse(person.is_active)

    def test_form_invalid(self):
        "It should not create a user, and should show the page again"
        response = self.client.post("/account/register/", {})
        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_honeypot(self):
        "If honeypot field is filled in, should not create a user"
        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "hello",
        }
        response = self.client.post("/account/register/", data)

        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_registration_question_correct(self):
        "If registration question is set, and used correctly, user should be created"
        ConfigFactory(
            use_registration_question=True,
            registration_question="Who?",
            registration_answer="elizabeth",
        )

        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "",
            "answer": "Elizabeth",
        }
        response = self.client.post("/account/register/", data)

        person = Person.objects.first()
        self.assertRedirects(response, "/account/register/complete/")
        self.assertEqual(person.name, "Bob")

    def test_registration_question_incorrect(self):
        "If registration question is not used correctly, user should not be created"
        ConfigFactory(
            use_registration_question=True,
            registration_question="Who?",
            registration_answer="elizabeth",
        )

        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "",
            "answer": "nope",
        }
        response = self.client.post("/account/register/", data)

        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_user_name_already_in_use(self):
        "If supplied name is already used, user should not be created"
        PersonFactory(name="bob")

        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "",
        }
        response = self.client.post("/account/register/", data)

        # Only the existing person should be there:
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_email_already_in_use(self):
        "If supplied email is already used, user should not be created"
        PersonFactory(email="BOB@EXAMPLE.COM")

        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "",
        }
        response = self.client.post("/account/register/", data)

        # Only the existing person should be there:
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_passwords_not_the_same(self):
        "If supplied passwords are not the same, user should not be created"
        data = {
            "name": "Bob",
            "password1": "MY-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "",
        }
        response = self.client.post("/account/register/", data)

        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_registration_not_allowed(self):
        "If registration is not allowed in Config, user should not be created"
        ConfigFactory(allow_registration=False)

        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@example.com",
            "url": "",
            "honeypot": "",
        }
        response = self.client.post("/account/register/", data)

        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    # From when we used django-recaptcha on the registration form.
    # Not sure how to test django-hCaptcha here instead.
    # @patch("captcha.fields.client.submit")
    # def test_recaptcha_enabled(self, mocked_submit):
    #     """Ensure registration works if captcha is enabled.
    #     Can't really test the ReCaptcha itself, so mocking it so it's not required.
    #     Following an example at https://github.com/praekelt/django-recaptcha/blob/develop/captcha/tests/test_fields.py  # noqa: E501
    #     """
    #     ConfigFactory(use_registration_captcha=True)
    #     mocked_submit.return_value = RecaptchaResponse(is_valid=True)

    #     data = {
    #         "name": "Bob",
    #         "password1": "my-password-123",
    #         "password2": "my-password-123",
    #         "email": "bob@example.com",
    #         "url": "",
    #         "honeypot": "",
    #         "g-recaptcha-response": "PASSED",
    #     }
    #     response = self.client.post("/account/register/", data)

    #     self.assertEqual(Person.objects.count(), 1)
    #     self.assertRedirects(response, "/account/register/complete/")

    def test_validate_disallowed_names(self):
        "We should not be able to register with a disallowed name"
        # Not testing every disallowed name, but a sample from
        # membership.utilities.validate_person_name()
        # Matching the first test in there.
        names = ["anon", "Samuel Pepys", "  root  "]

        for name in names:
            data = {
                "name": name,
                "password1": "my-password-123",
                "password2": "my-password-123",
                "email": "bob@example.com",
                "url": "",
                "honeypot": "",
            }
            response = self.client.post("/account/register/", data)
            self.assertEqual(Person.objects.count(), 0)
            self.assertEqual(response.status_code, 200)
            errors = response.context["form"].errors.as_data()
            self.assertEqual(
                f"{name.strip()} is not an available name",
                str(errors["name"][0].message),
            )

    def test_validate_disallowed_names_2(self):
        "We should not be able to register with a disallowed name"
        # Not testing every disallowed name, but a sample from
        # membership.utilities.validate_person_name()
        # Matching the second test in there.
        names = ["()"]
        for name in names:
            data = {
                "name": name,
                "password1": "my-password-123",
                "password2": "my-password-123",
                "email": "bob@example.com",
                "url": "",
                "honeypot": "",
            }
            response = self.client.post("/account/register/", data)
            self.assertEqual(Person.objects.count(), 0)
            self.assertEqual(response.status_code, 200)
            errors = response.context["form"].errors.as_data()
            self.assertEqual(
                f"{name.strip()} contains invalid characters or formatting",
                str(errors["name"][0].message),
            )

    @override_settings(PEPYS_MEMBERSHIP_BLACKLISTED_DOMAINS=["evildomain.com"])
    def test_blacklisted_domains(self):
        "It should silently fail to create the user, as if it worked"
        data = {
            "name": "Bob",
            "password1": "my-password-123",
            "password2": "my-password-123",
            "email": "bob@evildomain.com",
            "url": "https://example.com",
            "honeypot": "",
        }
        response = self.client.post("/account/register/", data)

        self.assertEqual(Person.objects.count(), 0)
        self.assertRedirects(response, "/account/register/complete/")

    def test_bad_urls(self):
        "It should silently fail to create the user, as if it worked"
        bad_urls = [
            "http://123.123.255.0",
            "https://123.123.255.0",
            "https://123.123.255.0/foo",
        ]
        for url in bad_urls:
            data = {
                "name": "Bob",
                "password1": "my-password-123",
                "password2": "my-password-123",
                "email": "bob@example.com",
                "url": url,
                "honeypot": "",
            }
            response = self.client.post("/account/register/", data)

            self.assertEqual(Person.objects.count(), 0)
            self.assertRedirects(response, "/account/register/complete/")


class RegisterCompleteViewTestCase(LoginTestCase):
    def test_response_200(self):
        response = self.client.get("/account/register/complete/")
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get("/account/register/complete/")
        self.assertEqual(response.template_name[0], "membership/message.html")

    def test_redirects_if_user_is_logged_in(self):
        self.log_user_in()
        response = self.client.get("/account/register/complete/")
        self.assertRedirects(response, "/")
