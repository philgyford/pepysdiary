import factory
import pytz

from pepysdiary.indepth.models import Article


class AbstractArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
        abstract = True

    title = factory.Faker("text", max_nb_chars=100)
    text = "<p>A test article.</p>"


class DraftArticleFactory(AbstractArticleFactory):
    status = Article.Status.DRAFT


class PublishedArticleFactory(AbstractArticleFactory):
    status = Article.Status.PUBLISHED
    date_published = factory.Faker("past_datetime", start_date="-30d", tzinfo=pytz.utc)
