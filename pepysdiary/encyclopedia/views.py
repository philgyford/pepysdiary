from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from pepysdiary.encyclopedia.models import Category, Topic


class EncyclopediaView(TemplateView):
    template_name = 'category_list.html'

    def get_context_data(self, **kwargs):
        context = super(EncyclopediaView, self).get_context_data(**kwargs)
        context['categories'] = Category.get_annotated_list()
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
