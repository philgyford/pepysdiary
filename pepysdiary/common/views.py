from django.core.urlresolvers import reverse
from django.views.generic import RedirectView


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
