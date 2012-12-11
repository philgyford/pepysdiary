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
