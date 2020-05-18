from django.conf.urls import url

from pepysdiary.membership.views import (
    LoginView,
    LogoutView,
    RegisterView,
    RegisterCompleteView,
    ActivationCompleteView,
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
    url(r"^login/$", LoginView.as_view(), name="login"),
    url(r"^logout/$", LogoutView.as_view(), name="logout"),
    url(r"^register/$", RegisterView.as_view(), name="register"),
    url(
        r"^register/complete/$",
        RegisterCompleteView.as_view(),
        name="register_complete",
    ),
    url(
        r"^activate/complete/$",
        ActivationCompleteView.as_view(),
        name="activate_complete",
    ),
    url(
        r"^activate/(?P<activation_key>[\w]+)/$",
        ActivateView.as_view(),
        name="activate",
    ),
    url(r"^edit/$", EditProfileView.as_view(), name="edit_profile"),
    # A user viewing themselves:
    url(r"^profile/$", PrivateProfileView.as_view(), name="private_profile"),
    # A public user profile page:
    url(r"^profile/(?P<pk>[\d]+)/$", ProfileView.as_view(), name="profile"),
    url(r"^password/reset/$", PasswordResetView.as_view(), name="password_reset"),
    url(
        r"^password/reset/done/$",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    url(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",  # noqa: E501
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    url(
        r"^password/reset/complete/$",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
