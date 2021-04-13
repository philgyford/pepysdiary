import factory
import pytz

from pepysdiary.news.models import Post


class AbstractPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        abstract = True

    title = factory.Faker("text", max_nb_chars=100)
    intro = factory.Faker("paragraph")
    text = factory.Faker("paragraph")


class DraftPostFactory(AbstractPostFactory):
    status = Post.Status.DRAFT


class PublishedPostFactory(AbstractPostFactory):
    status = Post.Status.PUBLISHED
    date_published = factory.Faker("past_datetime", start_date="-30d", tzinfo=pytz.utc)
