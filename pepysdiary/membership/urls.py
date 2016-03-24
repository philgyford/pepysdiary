# coding: utf-8
from django.conf.urls import *

from pepysdiary.membership.forms import PasswordResetForm, SetPasswordForm
from pepysdiary.membership.views import *


urlpatterns = [

    url(r'^login/$', login, name='login'),

    url(r'^logout/$', logout, name='logout'),

    url(r'^register/$', RegisterView.as_view(), name='register'),

    url(r'^register/complete/$', RegisterCompleteView.as_view(),
                                                    name='register_complete'),

    url(r'^activate/complete/$', ActivationCompleteView.as_view(),
                                                    name='activate_complete'),

    url(r'^activate/(?P<activation_key>[\w]+)/$', ActivateView.as_view(),
                                                            name='activate'),

    url(r'^edit/$', EditProfileView.as_view(), name='edit_profile'),

    # A user viewing themselves:
    url(r'^profile/$', PrivateProfileView.as_view(), name='private_profile'),

    # A public user profile page:
    url(r'^profile/(?P<pk>[\d]+)/$', ProfileView.as_view(), name='profile'),

    url(r'^password/reset/$',
        password_reset, {
            'template_name': 'password_reset.html',
            'password_reset_form': PasswordResetForm,
            'email_template_name': 'emails/password_reset.txt'
        }, 'password_reset'),

    url(r'^password/reset/done/$',
        password_reset_done, {
            'template_name': 'message.html',
        }, 'password_reset_done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, {
            'template_name': 'password_confirm.html',
            'set_password_form': SetPasswordForm,
        }, 'password_reset_confirm'),

    url(r'^password/reset/complete/$',
        password_reset_complete, {
            'template_name': 'message.html',
        }, 'password_reset_complete'),
]
