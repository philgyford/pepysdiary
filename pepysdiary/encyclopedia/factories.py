import factory
from pepysdiary.encyclopedia import models
from pepysdiary.encyclopedia import category_lookups


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    title = factory.Faker('sentence', nb_words=2)
    slug = factory.Faker('slug')
    depth = 1

    

class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic

    title = factory.Faker('sentence', nb_words=4)

    summary = factory.Faker('paragraph', nb_sentences=2)
    wheatley = factory.Faker('sentence', nb_words=20)
    tooltip_text = factory.Faker('sentence', nb_words=20)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of categories were passed in, use them
            for category in extracted:
                self.categories.add(category)


class PersonTopicFactory(TopicFactory):

    title = factory.Faker('name')

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
            # Adding the category with an ID of 2, which is People:
            self.categories.add(CategoryFactory(id=category_lookups.PEOPLE))
    

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
            self.categories.add(CategoryFactory(id=category_lookups.PLACES))
    
