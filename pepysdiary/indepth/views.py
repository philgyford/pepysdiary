from django.http import Http404
from django.views.generic.dates import DateDetailView

from pepysdiary.common.views import PaginatedListView
from .models import Article


class ArticleArchiveView(PaginatedListView):
    model = Article
    queryset = Article.published_articles.all()
    paginate_by = 10
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Article.Category.choices
        return context


class ArticleCategoryArchiveView(PaginatedListView):
    """
    All the Articles in one In-depth Articles Category.
    """

    model = Article
    template_name_suffix = "_category_list"
    paginate_by = 10
    allow_empty = True
    # Will be set in get():
    category = None

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        return Article.published_articles.filter(category=self.category)

    def get(self, request, *args, **kwargs):
        """
        Check we have a valid category slug before doing anything else.
        """
        slug = kwargs.get("category_slug", None)
        if Article.is_valid_category_slug(slug):
            self.category = slug
        else:
            raise Http404("Invalid category slug: '%s'." % slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_slug"] = self.category
        context["category_name"] = Article.category_slug_to_name(self.category)
        context["categories"] = Article.Category.choices
        return context


class ArticleDetailView(DateDetailView):
    """
    Note: This generates Runtime Errors because we're using a DateTime field
    (date_published) rather than a Date field, and this ends up using
    naive datetimes.
    https://code.djangoproject.com/ticket/18794
    https://docs.djangoproject.com/en/dev/ref/class-based-views/mixins-date-based/#datemixin
    """

    model = Article
    date_field = "date_published"
    queryset = Article.published_articles.all()
    year_format = "%Y"
    month_format = "%m"
    day_format = "%d"

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context["categories"] = Article.Category.choices
        extra_context = self.get_next_previous()
        context.update(extra_context)
        return context

    def get_next_previous(self):
        """
        Get the next/previous Articles based on the current Article's date.
        """
        try:
            previous_article = (
                self.model.published_articles.filter(
                    date_published__lt=self.object.date_published
                )
                .order_by("-date_published")[:1]
                .get()
            )
        except self.model.DoesNotExist:
            previous_article = None

        try:
            next_article = (
                self.model.published_articles.filter(
                    date_published__gt=self.object.date_published
                )
                .order_by("date_published")[:1]
                .get()
            )
        except self.model.DoesNotExist:
            next_article = None

        return {
            "previous_article": previous_article,
            "next_article": next_article,
        }
