import shlex
import smartypants

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.sites.models import Site
from django.contrib.syndication.views import add_domain, Feed
from django.db.models import F
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import strip_tags
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, RedirectView
from django.views.generic.base import TemplateView

from pepysdiary.common.utilities import ExtendedRSSFeed
from pepysdiary.diary.models import Entry
from pepysdiary.encyclopedia.models import Topic
from pepysdiary.letters.models import Letter
from pepysdiary.news.models import Post


class CacheMixin(object):
    """
    Add this mixin to a class-based view to specify caching.
    Set the cache_timeout on the view to change the timeout.
    """
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super().dispatch)(*args, **kwargs)


class HomeView(TemplateView):
    """Front page of the whole site."""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Show the most recent "published" entries:
        # If we change the number of Entries, the template will need tweaking
        # too...
        context['entry_list'] = Entry.objects.filter(
                diary_date__lte=Entry.objects.most_recent_entry_date()
            ).order_by('-diary_date')[:8]

        context['tooltip_references'] = Entry.objects.get_brief_references(
                                                objects=context['entry_list'])

        context['post_list'] = Post.published_posts.all()[:2]
        return context


class GoogleSearchView(TemplateView):
    """Legacy view/template that uses Google's site search to provide search
    results via JavaScript.
    """
    template_name = 'search_google.html'


class SearchView(ListView):
    """For searching different kinds of models.

    Curently works for:
    * Entry

    GET arguments allowed:
        * 'q': The search term(s)
        * 'k': Kind; which model to search. Valid values are:
            * 'd': Diary Entry (default)
            * 'l': Letter
            * 't': Topic
        * 'o': Order; how to order results. Valid values are:
            * 'r': Relevancy (default)
            * 'da': Date ascending (Entry, Letter)
            * 'dd': Date descending (Entry, Letter)
            * 'az': Title ascending (Topic)
    """
    template_name = 'search.html'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        """Before the parent's dispatch() method, set self.model based on
        supplied GET args.
        """
        self.set_model()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query_string = self.get_search_query_string()

        if query_string == '':
            queryset = self.model.objects.none()
        else:
            query = SearchQuery(query_string)

            queryset = self.model.objects.filter(search_document=query)

            ordering = self.get_ordering()
            if ordering:
                if ordering == '-rank' or ordering == 'rank':
                    # Need to annotate the queryset to display in rank order.
                    # Assumes that all our searchable models have a search_document
                    # attribute that's a SearchVectorField().
                    rank_annotation = SearchRank(
                                               F('search_document'), query)
                    queryset = queryset.annotate(rank=rank_annotation)
                queryset = queryset.order_by(ordering)

        return queryset

    def set_model(self):
        """Work out what model we're searching, based on the 'k' GET arg.
        """
        kind = self.request.GET.get('k', '').strip()

        if kind == 'd':
            self.model = Entry
        elif kind == 'l':
            self.model = Letter
        elif kind == 't':
            self.model = Topic
        else:
            self.model = Entry

    def get_search_query_string(self):
        return self.request.GET.get('q', '').strip()

    def get_ordering(self):
        """Get the order for the queryset, based on the 'o' GET arg.
        Assumes we've set self.model already, as orders are model-specific.
        """
        order_string = self.request.GET.get('o', '').strip()

        # Default, order by most-relevant first:
        order = '-rank'

        if self.model == Entry:
            if order_string == 'da':
                order = 'diary_date'
            elif order_string == 'dd':
                order = '-diary_date'
        elif self.model == Letter:
            if order_string == 'da':
                order = 'letter_date'
            elif order_string == 'dd':
                order = '-letter_date'
        elif self.model == Topic:
            if order_string == 'az':
                order = 'order_title'

        return order


class RecentView(CacheMixin, TemplateView):
    """Recent Activity page."""
    cache_timeout = (60 * 5)
    template_name = 'recent.html'


class BaseRSSFeed(Feed):
    feed_type = ExtendedRSSFeed

    link = '/'
    # Children should also have:
    # title
    # description

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}

    def item_title(self, item):
        return force_text(item.title)

    def item_pubdate(self, item):
        return item.date_published

    def item_author_name(self, item):
        return 'Phil Gyford'

    def make_item_description(self, text):
        "Called by item_description() in children."
        length = 250
        text = strip_tags(text)
        if len(text) <= length:
            return force_text(text)
        else:
            return ' '.join(text[:length + 1].split(' ')[0:-1]) + '...'

    def make_item_content_encoded(self, text1, text2, url, comment_name):
        """
        Called from item_content_encoded() in children.
        text1 and text2 are chunks of HTML text (or empty strings).
        url is the URL of the item (no domain needed, eg '/diary/1666/10/31/').
        comment_name is one of 'comment' or 'annotation'.
        """
        return '%s %s <p><strong><a href="%s#%ss">Read the %ss</a></strong></p>' % (
            force_text(smartypants.smartypants(text1)),
            force_text(smartypants.smartypants(text2)),
            add_domain(Site.objects.get_current().domain, url),
            comment_name,
            comment_name
        )


# ALL THE REDIRECT VIEWS:

class DiaryMonthRedirectView(RedirectView):
    """
    To help with redirecting from old /archive/1660/01/ URLs to the
    new Diary Month URLs.
    """
    def get_redirect_url(self, year, month):
        return reverse('entry_month_archive', kwargs={
                                                'year': year, 'month': month})


class DiaryEntryRedirectView(RedirectView):
    """
    To help with redirecting from old /archive/1660/01/01/index.php URLs to the
    new Diary Entry URLs.
    """
    def get_redirect_url(self, year, month, day):
        return reverse('entry_detail', kwargs={
                                    'year': year, 'month': month, 'day': day})


class EncyclopediaCategoryRedirectView(RedirectView):
    """
    To redirect from old /background/cat/subcat1/subcat2.php URLs to the new
    Category URLs.
    """
    def get_redirect_url(self, slugs):
        slugs = slugs.replace('_', '-')
        return reverse('category_detail', kwargs={'slugs': slugs})


class EncyclopediaTopicRedirectView(RedirectView):
    """
    To help with redirecting from old /p/348.php URLs to the new Topic URLs.
    """
    def get_redirect_url(self, pk):
        return reverse('topic_detail', kwargs={'pk': int(pk)})


class LetterRedirectView(RedirectView):
    """
    To help with redirecting from old /letter/1660/01/01/slug-field.php URLs
    to the new Letter URLs.
    """
    def get_redirect_url(self, year, month, day, slug):
        return reverse('letter_detail', kwargs={
            'year': year, 'month': month, 'day': day, 'slug': slug, })


class ArticleRedirectView(RedirectView):
    """
    To help with redirecting from old
    /indepth/archive/2012/05/31/slug_field.php URLs to the new Article URLs.
    """
    def get_redirect_url(self, year, month, day, slug):
        slug = slug.replace('_', '-')
        return reverse('article_detail', kwargs={
            'year': year, 'month': month, 'day': day, 'slug': slug, })


class PostRedirectView(RedirectView):
    """
    To help with redirecting from old
    /about/archive/2012/05/31/3456/ URLs to the new News Post URLs.
    """
    def get_redirect_url(self, year, month, day, pk):
        return reverse('post_detail', kwargs={
            'year': year, 'month': month, 'day': day, 'pk': pk, })


class SummaryYearRedirectView(RedirectView):
    """
    To help with redirecting from old
    /about/history/1660/ URLs to the new Summary URLs.
    """
    def get_redirect_url(self, year):
        return reverse('summary_year_archive', kwargs={'year': year, })
