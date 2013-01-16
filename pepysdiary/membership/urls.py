from django.conf.urls import *

from pepysdiary.membership.views import *


urlpatterns = patterns('',

    url(r'^login/$', login, name='login'),

    url(r'^register/$', RegisterView.as_view(), name='register'),

    url(r'^register/complete/$', RegisterCompleteView.as_view(),
                                                    name='register_complete'),

    url(r'^activate/complete/$', ActivationCompleteView.as_view(),
                                                    name='activate_complete'),

    url(r'^activate/(?P<activation_key>[\w]+)/$', ActivateView.as_view(),
                                                            name='activate'),

)
