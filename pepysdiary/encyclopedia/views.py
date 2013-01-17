from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from pepysdiary.common.views import BaseRSSFeed
from pepysdiary.encyclopedia.models import Category, Topic


class EncyclopediaView(TemplateView):
    template_name = 'category_list.html'

    def get_context_data(self, **kwargs):
        context = super(EncyclopediaView, self).get_context_data(**kwargs)
        context['categories'] = Category.get_annotated_list()
        context['topic_count'] = Topic.objects.count()
        return context


class CategoryDetailView(DetailView):
    model = Category
    slug_url_kwarg = 'slugs'

    def get_object(self, queryset=None):
        slugs = self.kwargs.get(self.slug_url_kwarg, None)
        if slugs is not None:
            try:
                slug = slugs.split('/')[-1]
            except:
                raise Http404(_(u"No Category slug found"))
        else:
            raise AttributeError(u'CategoryDetailView must be called with '
                                    'slugs in the URL')

        try:
            obj = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise Http404(_(u"No Categories found matching the query"))
        return obj


class TopicDetailView(DetailView):
    model = Topic

    def get_context_data(self, **kwargs):
        context = super(TopicDetailView, self).get_context_data(**kwargs)
        context['diary_references'] = \
                                self.object.get_annotated_diary_references()
        return context


class LatestTopicsFeed(BaseRSSFeed):
    title = "Pepys' Diary - Encyclopedia Topics"
    description = "New topics about Samuel Pepys and his world"

    def items(self):
        return Topic.objects.all().order_by('-date_created')[:8]

    def item_pubdate(self, item):
        return item.date_created

    def item_description(self, item):
        if item.summary_html:
            return self.make_item_description(item.summary_html)
        elif item.wheatley_html:
            return self.make_item_description(item.wheatley_html)
        elif item.tooltip_text:
            return self.make_item_description(item.tooltip_text)
        else:
            return ''

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            text1=item.summary_html,
            text2=item.wheatley_html,
            url=item.get_absolute_url(),
            comment_name=item.comment_name
        )
