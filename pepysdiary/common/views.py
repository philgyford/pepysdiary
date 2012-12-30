from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

from pepysdiary.diary.models import Entry
from pepysdiary.news.models import Post


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Show the most recent "published" entries:
        context['entry_list'] = Entry.objects.filter(
                diary_date__lte=Entry.objects.most_recent_entry_date
            ).order_by('-diary_date')[:7]

        context['post_list'] = Post.published_posts.all()[:2]
        return context


class DiaryEntryRedirectView(RedirectView):
    """
    To help with redirecting from old /archive/1660/01/01/index.php URLs to the
    new Diary Entry URLs.
    """
    def get_redirect_url(self, year, month, day):
        return reverse('diary_entry', kwargs={
            'year': year, 'month': month, 'day': day})


class EncyclopediaCategoryRedirectView(RedirectView):
    """
    To redirect from old /background/cat/subcat1/subcat2.php URLs to the new
    Category URLs.
    """
    def get_redirect_url(self, slugs):
        slugs = slugs.replace('_', '-')
        return reverse('encyclopedia_category', kwargs={'slugs': slugs})


class EncyclopediaTopicRedirectView(RedirectView):
    """
    To help with redirecting from old /p/348.php URLs to the new Topic URLs.
    """
    def get_redirect_url(self, pk):
        return reverse('encyclopedia_topic', kwargs={'pk': pk})


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
