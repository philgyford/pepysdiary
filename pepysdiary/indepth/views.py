from django.views.generic.dates import DateDetailView

from pepysdiary.indepth.models import Article


class ArticleDetailView(DateDetailView):
    model = Article
    date_field = 'date_published'
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'
