from django.conf.urls.defaults import *

from pepysdiary.encyclopedia.views import *


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', TopicDetailView.as_view(),
                                                    name='encyclopedia_topic'),
)
