from django.http import Http404
from django.views.generic.dates import DateDetailView

from pepysdiary.common.views import PaginatedListView

from .models import Post


class PostArchiveView(PaginatedListView):
    """
    The front page of the Site News section.
    """

    model = Post
    queryset = Post.published_posts.all()
    paginate_by = 10
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Post.Category.choices
        return context


class PostCategoryArchiveView(PaginatedListView):
    """
    All the Posts in one Site News Category.
    """

    model = Post
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
        return Post.published_posts.filter(category=self.category)

    def get(self, request, *args, **kwargs):
        """
        Check we have a valid category slug before doing anything else.
        """
        slug = kwargs.get("category_slug", None)
        if Post.is_valid_category_slug(slug):
            self.category = slug
        else:
            raise Http404("Invalid category slug: '%s'." % slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_slug"] = self.category
        context["category_name"] = Post.category_slug_to_name(self.category)
        context["categories"] = Post.Category.choices
        return context


class PostDetailView(DateDetailView):
    """
    Note: This generates Runtime Errors because we're using a DateTime field
    (date_published) rather than a Date field, and this ends up using
    naive datetimes.
    https://code.djangoproject.com/ticket/18794
    https://docs.djangoproject.com/en/dev/ref/class-based-views/mixins-date-based/#datemixin
    """

    model = Post
    date_field = "date_published"
    queryset = Post.published_posts.all()
    year_format = "%Y"
    month_format = "%m"
    day_format = "%d"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Post.Category.choices
        extra_context = self.get_next_previous()
        context.update(extra_context)
        return context

    def get_next_previous(self):
        """
        Get the next/previous Posts based on the current Post's date.
        """
        try:
            previous_post = (
                self.model.published_posts.filter(
                    date_published__lt=self.object.date_published
                )
                .order_by("-date_published")[:1]
                .get()
            )
        except self.model.DoesNotExist:
            previous_post = None

        try:
            next_post = (
                self.model.published_posts.filter(
                    date_published__gt=self.object.date_published
                )
                .order_by("date_published")[:1]
                .get()
            )
        except self.model.DoesNotExist:
            next_post = None

        return {
            "previous_post": previous_post,
            "next_post": next_post,
        }
