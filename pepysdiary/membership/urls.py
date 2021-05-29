from django.urls import path, re_path

from pepysdiary.membership.views import (
    LoginView,
    LogoutView,
    RegisterView,
    RegisterCompleteView,
    ActivateCompleteView,
    ActivateView,
    EditProfileView,
    PrivateProfileView,
    ProfileView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "register/complete/",
        RegisterCompleteView.as_view(),
        name="register_complete",
    ),
    path(
        "activate/complete/",
        ActivateCompleteView.as_view(),
        name="activate_complete",
    ),
    re_path(
        r"^activate/(?P<activation_key>[\w]+)/$",
        ActivateView.as_view(),
        name="activate",
    ),
    path("edit/", EditProfileView.as_view(), name="edit_profile"),
    # A user viewing themselves:
    path("profile/", PrivateProfileView.as_view(), name="private_profile"),
    # A public user profile page:
    re_path(r"^profile/(?P<pk>[\d]+)/$", ProfileView.as_view(), name="profile"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/done/",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
