import factory
import pytz

from django.utils.text import slugify

from pepysdiary.indepth.models import Article


class AbstractArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
        abstract = True

    title = factory.Faker("text", max_nb_chars=100)
    text = "<p>A test article.</p>"
    slug = factory.LazyAttribute(lambda o: slugify(o.title)[:50])


class DraftArticleFactory(AbstractArticleFactory):
    status = Article.Status.DRAFT


class PublishedArticleFactory(AbstractArticleFactory):
    status = Article.Status.PUBLISHED
    date_published = factory.Faker("past_datetime", start_date="-30d", tzinfo=pytz.utc)
