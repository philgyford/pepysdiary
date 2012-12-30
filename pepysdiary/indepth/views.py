from django.views.generic.dates import DateDetailView
from django.views.generic.list import ListView

from pepysdiary.common.views import BaseRSSFeed
from pepysdiary.indepth.models import Article


class ArticleDetailView(DateDetailView):
    """
    Note: This generates Runtime Errors because we're using a DateTime field
    (date_published) rather than a Date field, and this ends up using
    naive datetimes.
    https://code.djangoproject.com/ticket/18794
    https://docs.djangoproject.com/en/dev/ref/class-based-views/mixins-date-based/#datemixin
    """
    model = Article
    date_field = 'date_published'
    queryset = Article.published_articles.all()
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        extra_context = self.get_next_previous()
        context.update(extra_context)
        return context

    def get_next_previous(self):
        """
        Get the next/previous Articles based on the current Article's date.
        """
        try:
            previous_article = self.model.published_articles.filter(
                                date_published__lt=self.object.date_published
                            ).order_by('-date_published')[:1].get()
        except self.model.DoesNotExist:
            previous_article = None

        try:
            next_article = self.model.published_articles.filter(
                                date_published__gt=self.object.date_published
                            ).order_by('date_published')[:1].get()
        except self.model.DoesNotExist:
            next_article = None

        return {
            'previous_article': previous_article,
            'next_article': next_article,
        }


class ArticleArchiveView(ListView):
    model = Article
    queryset = Article.published_articles.all()


class LatestArticlesFeed(BaseRSSFeed):
    title = "Pepys' Diary - In-Depth Articles"
    description = "Articles about Samuel Pepys and his world"

    def items(self):
        return Article.published_articles.all().order_by('-date_published')[:2]

    def item_description(self, item):
        return self.make_item_description(item.intro_html)

    def item_content_encoded(self, item):
        return self.make_item_content_encoded(
            text1=item.intro_html,
            text2=item.text_html,
            url=item.get_absolute_url(),
            comment_name='annotation')
