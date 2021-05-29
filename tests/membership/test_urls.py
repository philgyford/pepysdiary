from django.test import TestCase
from django.urls import resolve, reverse

from pepysdiary.membership import views


class MembershipURLsTestCase(TestCase):
    """Testing that the named URLs map the correct name to URL,
    and that the correct views are called.
    """

    def test_login_url(self):
        self.assertEqual(reverse("login"), "/account/login/")

    def test_login_view(self):
        self.assertEqual(
            resolve("/account/login/").func.__name__, views.LoginView.__name__
        )

    def test_logout_url(self):
        self.assertEqual(reverse("logout"), "/account/logout/")

    def test_logout_view(self):
        self.assertEqual(
            resolve("/account/logout/").func.__name__, views.LogoutView.__name__
        )

    def test_register_url(self):
        self.assertEqual(reverse("register"), "/account/register/")

    def test_register_view(self):
        self.assertEqual(
            resolve("/account/register/").func.__name__, views.RegisterView.__name__
        )

    def test_register_complete_url(self):
        self.assertEqual(reverse("register_complete"), "/account/register/complete/")

    def test_register_complete_view(self):
        self.assertEqual(
            resolve("/account/register/complete/").func.__name__,
            views.RegisterCompleteView.__name__,
        )

    def test_activate_complete_url(self):
        self.assertEqual(reverse("activate_complete"), "/account/activate/complete/")

    def test_activate_complete_view(self):
        self.assertEqual(
            resolve("/account/activate/complete/").func.__name__,
            views.ActivateCompleteView.__name__,
        )

    def test_edit_profile_url(self):
        self.assertEqual(reverse("edit_profile"), "/account/edit/")

    def test_edit_profile_view(self):
        self.assertEqual(
            resolve("/account/edit/").func.__name__, views.EditProfileView.__name__
        )

    def test_private_profile_url(self):
        self.assertEqual(reverse("private_profile"), "/account/profile/")

    def test_private_profile_view(self):
        self.assertEqual(
            resolve("/account/profile/").func.__name__,
            views.PrivateProfileView.__name__,
        )

    def test_profile_url(self):
        self.assertEqual(
            reverse("profile", kwargs={"pk": "123"}), "/account/profile/123/"
        )

    def test_profile_view(self):
        self.assertEqual(
            resolve("/account/profile/123/").func.__name__, views.ProfileView.__name__
        )

    def test_password_reset_url(self):
        self.assertEqual(reverse("password_reset"), "/account/password/reset/")

    def test_password_reset_view(self):
        self.assertEqual(
            resolve("/account/password/reset/").func.__name__,
            views.PasswordResetView.__name__,
        )

    def test_password_reset_done_url(self):
        self.assertEqual(
            reverse("password_reset_done"), "/account/password/reset/done/"
        )

    def test_password_reset_done_view(self):
        self.assertEqual(
            resolve("/account/password/reset/done/").func.__name__,
            views.PasswordResetDoneView.__name__,
        )

    def test_password_reset_confirm_url(self):
        self.assertEqual(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": "123456abcdef", "token": "abcdef123456"},
            ),
            "/account/reset/123456abcdef/abcdef123456/",
        )

    def test_password_reset_confirm_view(self):
        self.assertEqual(
            resolve("/account/reset/123456abcdef/abcdef123456/").func.__name__,
            views.PasswordResetConfirmView.__name__,
        )

    def test_password_reset_complete_url(self):
        self.assertEqual(
            reverse("password_reset_complete"), "/account/password/reset/complete/"
        )

    def test_password_reset_complete_view(self):
        self.assertEqual(
            resolve("/account/password/reset/complete/").func.__name__,
            views.PasswordResetCompleteView.__name__,
        )
