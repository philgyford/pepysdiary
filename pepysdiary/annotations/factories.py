from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
import factory
import pytz

from pepysdiary.annotations.models import Annotation
from pepysdiary.diary.factories import EntryFactory
from pepysdiary.encyclopedia.factories import TopicFactory
from pepysdiary.indepth.factories import PublishedArticleFactory
from pepysdiary.news.factories import PublishedPostFactory
from pepysdiary.letters.factories import LetterFactory


class AbstractAnnotationFactory(factory.django.DjangoModelFactory):
    """
    Use a child class and pass in the content_object that the
    annotation is posted on (e.g. an Entry).
    """

    class Meta:
        model = Annotation
        abstract = True
        exclude = ["content_object"]

    user = factory.SubFactory("pepysdiary.membership.factories.PersonFactory")
    user_name = factory.LazyAttribute(
        lambda o: o.user.name if o.user and o.user.name else ""
    )
    user_email = factory.LazyAttribute(
        lambda o: o.user.email if o.user and o.user.email else ""
    )
    user_url = factory.LazyAttribute(
        lambda o: o.user.url if o.user and o.user.url else ""
    )
    comment = factory.Faker("paragraph")
    submit_date = factory.Faker("past_datetime", start_date="-30d", tzinfo=pytz.utc)
    is_public = True
    is_removed = False

    site = Site.objects.get_current()

    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    object_pk = factory.SelfAttribute("content_object.pk")


class ArticleAnnotationFactory(AbstractAnnotationFactory):
    "Pass in an Article as content_object to have the annotation on a specific Article"
    content_object = factory.SubFactory(PublishedArticleFactory)


class EntryAnnotationFactory(AbstractAnnotationFactory):
    "Pass in an Entry as content_object to have the annotation on a specific Entry"
    content_object = factory.SubFactory(EntryFactory)


class LetterAnnotationFactory(AbstractAnnotationFactory):
    "Pass in a Letter as content_object to have the annotation on a specific Letter"
    content_object = factory.SubFactory(LetterFactory)


class PostAnnotationFactory(AbstractAnnotationFactory):
    "Pass in a Post as content_object to have the annotation on a specific Post"
    content_object = factory.SubFactory(PublishedPostFactory)


class TopicAnnotationFactory(AbstractAnnotationFactory):
    "Pass in a Topic as content_object to have the annotation on a specific Topic"
    content_object = factory.SubFactory(TopicFactory)
