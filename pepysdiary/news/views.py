import smartypants

from django.contrib.sites.models import Site
from django.contrib.syndication.views import add_domain, Feed
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.html import escape, strip_tags
from django.views.generic.dates import DateDetailView
from django.views.generic.list import ListView

from pepysdiary.common.utilities import ExtendedRSSFeed
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
        context['categories'] = Post.CATEGORY_CHOICES
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


class PostCategoryArchiveView(ListView):
    """
    All the Posts in one Site News Category.
    """
    model = Post
    template_name_suffix = '_category_list'
    # Will be set in get():
    category = None

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.category is not None:
            queryset = Post.published_posts.filter(category=self.category)
        else:
            raise ImproperlyConfigured(
                                    "No possible queryset for this category.")
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Check we have a valid category slug before doing anything else.
        """
        slug = kwargs.get('category_slug', None)
        if Post.published_posts.is_valid_category_slug(slug):
            self.category = slug
        else:
            raise Http404("Invalid category slug: '%s'." % slug)
        return super(PostCategoryArchiveView, self).get(
                                                    request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostCategoryArchiveView, self).get_context_data(
                                                                    **kwargs)
        context['category_slug'] = self.category
        context['category_name'] = Post.published_posts.category_slug_to_name(
                                                                self.category)
        context['categories'] = Post.CATEGORY_CHOICES
        return context


class PostArchiveView(ListView):
    """
    The front page of the Site News section.
    """
    model = Post
    queryset = Post.published_posts.all()

    def get_context_data(self, **kwargs):
        context = super(PostArchiveView, self).get_context_data(**kwargs)
        context['categories'] = Post.CATEGORY_CHOICES
        return context


class LatestPostsFeed(Feed):
    feed_type = ExtendedRSSFeed

    link = '/'
    title = "Pepys' Diary - Site News"
    description = "News about the Pepys' Diary website"

    def items(self):
        return Post.published_posts.all().order_by('-date_published')[:3]

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}

    def item_title(self, item):
        return escape(force_unicode(item.title))

    def item_pubdate(self, item):
        return item.date_published

    def item_description(self, item):
        length = 250
        text = strip_tags(item.intro_html)
        if len(text) <= length:
            return force_unicode(text)
        else:
            return ' '.join(text[:length + 1].split(' ')[0:-1]) + '...'

    def item_author_name(self, item):
        return 'Phil Gyford'

    def item_content_encoded(self, item):
        return '<![CDATA[%s %s <p><strong><a href="%s#comments">Read the comments</a></strong></p>]>' % (
            force_unicode(smartypants.smartyPants(item.intro_html)),
            force_unicode(smartypants.smartyPants(item.text_html)),
            add_domain(Site.objects.get_current().domain,
                                                    item.get_absolute_url())
        )
