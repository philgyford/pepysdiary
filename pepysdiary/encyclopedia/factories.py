import factory
from faker import Faker

from django.db import IntegrityError

from pepysdiary.encyclopedia.models import Category, Topic
from pepysdiary.encyclopedia import category_lookups

fake = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    I think doing something like this creates a structure, and avoids
    errors about 'duplicate key value violates unique constraint
    "encyclopedia_category_path_key"':

        cat_1 = Category.add_root(title="Animals")
        cat_2 = cat_1.add_child(title="Dogs")
        cat_3 = cat_2.add_child(title="Terriers")
    """

    class Meta:
        model = Category

    title = factory.Faker("sentence", nb_words=2)
    slug = factory.Faker("slug")
    depth = 1


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    title = factory.Faker("sentence", nb_words=4)
    order_title = ""

    summary = factory.Faker("paragraph", nb_sentences=2)
    wheatley = factory.Faker("sentence", nb_words=20)
    tooltip_text = factory.Faker("sentence", nb_words=20)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of Categories were passed in, use them
            for category in extracted:
                self.categories.add(category)

    @factory.post_generation
    def diary_references(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of Entries were passed in, use them
            for entry in extracted:
                self.diary_references.add(entry)

    @factory.post_generation
    def letter_references(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of Letters were passed in, use them
            for letter in extracted:
                self.letter_references.add(letter)


class PersonTopicFactory(TopicFactory):

    title = factory.LazyAttribute(lambda p: "{} {}".format(fake.prefix(), fake.name()))

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of categories were passed in, use them
            for category in extracted:
                self.categories.add(category)
        else:
            try:
                # Adding the category with an ID of 2, which is People:
                self.categories.add(CategoryFactory(id=category_lookups.PEOPLE))
            except IntegrityError:
                pass


class PlaceTopicFactory(TopicFactory):
    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of categories were passed in, use them
            for category in extracted:
                self.categories.add(category)
        else:
            # Adding the category with an ID of 3, which is Places:
            try:
                self.categories.add(CategoryFactory(id=category_lookups.PLACES))
            except IntegrityError:
                pass
