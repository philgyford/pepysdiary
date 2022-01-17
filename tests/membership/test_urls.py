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
        self.assertEqual(resolve("/account/login/").func.view_class, views.LoginView)

    def test_logout_url(self):
        self.assertEqual(reverse("logout"), "/account/logout/")

    def test_logout_view(self):
        self.assertEqual(resolve("/account/logout/").func.view_class, views.LogoutView)

    def test_register_url(self):
        self.assertEqual(reverse("register"), "/account/register/")

    def test_register_view(self):
        self.assertEqual(
            resolve("/account/register/").func.view_class, views.RegisterView
        )

    def test_register_complete_url(self):
        self.assertEqual(reverse("register_complete"), "/account/register/complete/")

    def test_register_complete_view(self):
        self.assertEqual(
            resolve("/account/register/complete/").func.view_class,
            views.RegisterCompleteView,
        )

    def test_activate_complete_url(self):
        self.assertEqual(reverse("activate_complete"), "/account/activate/complete/")

    def test_activate_complete_view(self):
        self.assertEqual(
            resolve("/account/activate/complete/").func.view_class,
            views.ActivateCompleteView,
        )

    def test_edit_profile_url(self):
        self.assertEqual(reverse("edit_profile"), "/account/edit/")

    def test_edit_profile_view(self):
        self.assertEqual(
            resolve("/account/edit/").func.view_class, views.EditProfileView
        )

    def test_private_profile_url(self):
        self.assertEqual(reverse("private_profile"), "/account/profile/")

    def test_private_profile_view(self):
        self.assertEqual(
            resolve("/account/profile/").func.view_class, views.PrivateProfileView
        )

    def test_profile_url(self):
        self.assertEqual(
            reverse("profile", kwargs={"pk": "123"}), "/account/profile/123/"
        )

    def test_profile_view(self):
        self.assertEqual(
            resolve("/account/profile/123/").func.view_class, views.ProfileView
        )

    def test_password_reset_url(self):
        self.assertEqual(reverse("password_reset"), "/account/password/reset/")

    def test_password_reset_view(self):
        self.assertEqual(
            resolve("/account/password/reset/").func.view_class, views.PasswordResetView
        )

    def test_password_reset_done_url(self):
        self.assertEqual(
            reverse("password_reset_done"), "/account/password/reset/done/"
        )

    def test_password_reset_done_view(self):
        self.assertEqual(
            resolve("/account/password/reset/done/").func.view_class,
            views.PasswordResetDoneView,
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
            resolve("/account/reset/123456abcdef/abcdef123456/").func.view_class,
            views.PasswordResetConfirmView,
        )

    def test_password_reset_complete_url(self):
        self.assertEqual(
            reverse("password_reset_complete"), "/account/password/reset/complete/"
        )

    def test_password_reset_complete_view(self):
        self.assertEqual(
            resolve("/account/password/reset/complete/").func.view_class,
            views.PasswordResetCompleteView,
        )
