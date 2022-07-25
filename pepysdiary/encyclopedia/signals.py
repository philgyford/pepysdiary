from django.db.models.signals import m2m_changed, post_delete, pre_delete

from .models import Category, Topic


def topic_categories_changed(sender, **kwargs):
    """
    When we add or remove categories on this topic, we need to re-set those
    categories' topic counts.
    """
    if kwargs["reverse"]:
        # We're changing a Category's topics, so set that Category's count.
        if kwargs["instance"] is not None:
            kwargs["instance"].set_topic_count()
    else:
        # We're changing the categories on a topic.
        if kwargs["action"] == "pre_clear":
            # Before we do anything,
            # store the PKs of the current categories on this topic.
            kwargs["instance"]._original_categories_pks = [
                c.pk for c in kwargs["instance"].categories.all()
            ]

        elif kwargs["action"] in ["post_add", "post_remove"]:
            # Finished the action, so now change the old and new categories'
            # topic counts.
            # The PKs of the categories the topic has now:
            new_pks = kwargs.get("pk_set", [])
            # Make a list of both the new and old categories' PKs:
            pks = kwargs["instance"]._original_categories_pks + list(
                set(new_pks) - set(kwargs["instance"]._original_categories_pks)
            )
            # For all the old and new categories, set the counts:
            for pk in pks:
                cat = Category.objects.get(pk=pk)
                cat.set_topic_count()


m2m_changed.connect(topic_categories_changed, sender=Topic.categories.through)


def topic_pre_delete(sender, **kwargs):
    """
    Before deleting the topic, store the categories it has so that...
    """
    kwargs["instance"]._original_categories_pks = [
        c.pk for c in kwargs["instance"].categories.all()
    ]


pre_delete.connect(topic_pre_delete, sender=Topic)


def topic_post_delete(sender, **kwargs):
    """
    ...after deleting the topic, we re-set its categories' topic counts.
    """
    for pk in kwargs["instance"]._original_categories_pks:
        cat = Category.objects.get(pk=pk)
        cat.set_topic_count()


post_delete.connect(topic_post_delete, sender=Topic)
