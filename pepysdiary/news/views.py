from django.views.generic.dates import DateDetailView
from django.views.generic.list import ListView

from pepysdiary.news.models import Post


class PostDetailView(DateDetailView):
    """
    Note: This generates Runtime Errors because we're using a DateTime field
    (date_published) rather than a Date field, and this ends up using
    naive datetimes.
    https://code.djangoproject.com/ticket/18794
    https://docs.djangoproject.com/en/dev/ref/class-based-views/mixins-date-based/#datemixin
    """
    model = Post
    date_field = 'date_published'
    queryset = Post.published_posts.all()
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        extra_context = self.get_next_previous()
        context.update(extra_context)
        return context

    def get_next_previous(self):
        """
        Get the next/previous Posts based on the current Post's date.
        """
        try:
            previous_post = self.model.published_posts.filter(
                                date_published__lt=self.object.date_published
                            ).order_by('-date_published')[:1].get()
        except self.model.DoesNotExist:
            previous_post = None

        try:
            next_post = self.model.published_posts.filter(
                                date_published__gt=self.object.date_published
                            ).order_by('date_published')[:1].get()
        except self.model.DoesNotExist:
            next_post = None

        return {
            'previous_post': previous_post,
            'next_post': next_post,
        }


class PostArchiveView(ListView):
    model = Post
    queryset = Post.published_posts.all()
