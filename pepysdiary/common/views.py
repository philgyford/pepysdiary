import smartypants

from django.contrib.sites.models import Site
from django.contrib.syndication.views import add_domain, Feed
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.html import escape, strip_tags
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

from pepysdiary.common.utilities import ExtendedRSSFeed
from pepysdiary.diary.models import Entry
from pepysdiary.news.models import Post


class HomeView(TemplateView):
    """Front page of the whole site."""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Show the most recent "published" entries:
        # If we change the number of Entries, the template will need tweaking
        # too...
        context['entry_list'] = Entry.objects.filter(
                diary_date__lte=Entry.objects.most_recent_entry_date
            ).order_by('-diary_date')[:8]

        context['tooltip_references'] = Entry.objects.get_brief_references(
                                                objects=context['entry_list'])

        context['post_list'] = Post.published_posts.all()[:2]
        return context

class SearchView(TemplateView):
    template_name = 'search.html'

class RecentView(TemplateView):
    """Recent Activity page."""
    template_name = 'recent.html'

    @method_decorator(cache_page(60 * 5))
    def dispatch(self, *args, **kwargs):
        return super(RecentView, self).dispatch(*args, **kwargs)


class BaseRSSFeed(Feed):
    feed_type = ExtendedRSSFeed

    link = '/'
    # Children should also have:
    # title
    # description

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}

    def item_title(self, item):
        return escape(force_unicode(item.title))

    def item_pubdate(self, item):
        return item.date_published

    def item_author_name(self, item):
        return 'Phil Gyford'

    def make_item_description(self, text):
        "Called by item_description() in children."
        length = 250
        text = strip_tags(text)
        if len(text) <= length:
            return force_unicode(text)
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
            force_unicode(smartypants.smartypants(text1)),
            force_unicode(smartypants.smartypants(text2)),
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
