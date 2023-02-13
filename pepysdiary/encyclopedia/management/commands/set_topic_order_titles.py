# coding: utf-8
from optparse import make_option

from django.core.management.base import BaseCommand

from pepysdiary.encyclopedia.models import Topic


class Command(BaseCommand):
    """
    Goes through ALL the Topics and sets their order_title.

    Usage:
    $ ./manage.py set_topic_order_titles
    """

    option_list = BaseCommand.option_list + (
        make_option(
            "--all",
            action="store_true",
            dest="all",
            default=True,
            help="Re-set all the order_titles for all Topics",
        ),
    )
    args = ""
    help = "Re-set all the order_titles for all Topics"

    def handle(self, *args, **options):
        for topic in Topic.objects.all():
            # print '%s %s' % (topic.pk, topic.title)
            # Because the order_title is set on save, we just need to save
            # each topic:
            topic.save()
