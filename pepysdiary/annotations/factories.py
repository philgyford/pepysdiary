from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
import factory
import pytz

from pepysdiary.annotations.models import Annotation
from pepysdiary.diary.factories import EntryFactory


class AbstractAnnotationFactory(factory.django.DjangoModelFactory):
    """
    Use a child class and pass in the content_object that the
    annotation is posted on (e.g. an Entry).
    """
    class Meta:
        model = Annotation
        abstract = True
        exclude = ['content_object']

    user = factory.SubFactory("pepysdiary.membership.factories.PersonFactory")
    user_name = factory.LazyAttribute(lambda o: o.user.name)
    user_email = factory.LazyAttribute(lambda o: o.user.email)
    user_url = factory.LazyAttribute(lambda o: o.user.url if o.user.url else "")
    comment = factory.Faker("paragraph")
    submit_date = factory.Faker("past_datetime", start_date="-30d", tzinfo=pytz.utc)
    is_public = True
    is_removed = False

    site = Site.objects.get_current()

    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    object_pk = factory.SelfAttribute("content_object.pk")


class EntryAnnotationFactory(AbstractAnnotationFactory):
    content_object = factory.SubFactory(EntryFactory)


# We could make subclasses for Annotations posted on other objects if necessary.
