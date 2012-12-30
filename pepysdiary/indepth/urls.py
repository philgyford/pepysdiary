from django.conf.urls.defaults import *

from pepysdiary.indepth.views import *


# ALL REDIRECTS are in common/urls.py.

urlpatterns = patterns('',

    url(r'^rss/$', LatestArticlesFeed(), name='article_rss'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
                        ArticleDetailView.as_view(), name='article_detail'),

    url(r'^$', ArticleArchiveView.as_view(), name='indepth'),
)
