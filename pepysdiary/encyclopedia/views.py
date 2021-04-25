import string

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, TemplateView
from django.views.generic.detail import DetailView

from pepysdiary.common.views import CacheMixin
from .forms import CategoryMapForm
from .models import Category, Topic


# If no ID is supplied to the Map, it displays Topics from this Category:
DEFAULT_MAP_CATEGORY_ID = 28


class EncyclopediaView(CacheMixin, TemplateView):
    cache_timeout = 60 * 60
    template_name = "category_list.html"

    def get_context_data(self, **kwargs):
        context = super(EncyclopediaView, self).get_context_data(**kwargs)
        context["categories"] = Category.get_annotated_list()
        context["topic_count"] = Topic.objects.count()
        return context


class CategoryDetailView(DetailView):
    model = Category
    slug_url_kwarg = "slugs"

    def get_object(self, queryset=None):
        slugs = self.kwargs.get(self.slug_url_kwarg, None)
        if slugs is not None:
            try:
                slug = slugs.split("/")[-1]
            except Exception:
                raise Http404(_("No Category slug found"))
        else:
            raise AttributeError(
                "CategoryDetailView must be called with " "slugs in the URL"
            )

        try:
            obj = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise Http404(_("No Categories found matching the query"))
        return obj

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)

        topics = self.object.topics.only("id", "order_title")

        #  Makes a list of unique letters. Each letter is only included if this
        # category has a topic starting with that letter.
        # eg, ['A', 'B', 'E', 'N', 'T']
        # List comprehension from
        # http://www.peterbe.com/plog/uniqifiers-benchmark
        seen = set()
        context["used_letters"] = [
            topic.order_title[0].upper()
            for topic in topics
            if topic.order_title[0].upper() not in seen
            and not seen.add(topic.order_title[0].upper())
        ]

        # Quicker than relying on category.topics.all() in the template.
        # And we can fetch only the fields we need.
        context["topics"] = topics

        context["all_letters"] = list(string.ascii_uppercase)

        return context


class TopicDetailView(DetailView):
    model = Topic

    def get_context_data(self, **kwargs):
        context = super(TopicDetailView, self).get_context_data(**kwargs)
        context["diary_references"] = self.object.get_annotated_diary_references()
        return context


@method_decorator([csrf_protect], name="dispatch")
class CategoryMapView(FormView):
    """
    Turned off caching on this because *maybe* it was the cause of
    403 errors about the page's CSRF token.
    """

    form_class = CategoryMapForm
    template_name = "category_map.html"

    # Will be a Category object.
    category = None

    # Default category:
    category_id = DEFAULT_MAP_CATEGORY_ID

    def get(self, request, *args, **kwargs):
        # Set the Category ID of Topics we're displaying.
        cat_id = self.kwargs.get("category_id", None)
        if cat_id is not None:
            if int(cat_id) not in Category.objects.valid_map_category_ids():
                return redirect("category_map")
            else:
                self.category_id = int(cat_id)

        # Set the Category of Topics we're displaying.
        try:
            self.category = Category.objects.get(pk=self.category_id)
        except Category.DoesNotExist:
            raise ImproperlyConfigured(
                "'%s' has an invalid category_id: '%s'"
                % (self.__class__.__name__, self.category_id)
            )

        return super(CategoryMapView, self).get(request, *args, **kwargs)

    def get_initial(self):
        return {
            "category": self.category_id,
        }

    def form_valid(self, form):
        # This ID will then be used to generate the success_url:
        self.category_id = form.cleaned_data.get("category")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("category_map", kwargs={"category_id": self.category_id})

    def get_context_data(self, **kwargs):
        kwargs = super(CategoryMapView, self).get_context_data(**kwargs)
        kwargs["category"] = self.category
        kwargs["valid_map_category_ids"] = Category.objects.valid_map_category_ids()
        kwargs["pepys_homes_ids"] = Topic.objects.pepys_homes_ids()
        # Get this Category's Topics with locations:
        topics = list(self.category.topics.exclude(latitude__isnull=True))
        # Add Pepys' homes to every map.
        kwargs["topics"] = topics + list(
            Topic.objects.filter(pk__in=kwargs["pepys_homes_ids"])
        )
        return kwargs
