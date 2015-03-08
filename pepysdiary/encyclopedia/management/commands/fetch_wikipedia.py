# coding: utf-8
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from pepysdiary.encyclopedia.models import Topic


class Command(BaseCommand):
    args = '<topic_id topic_id ...>'
    help = "Fetches Wikipedia content Topics that have it"

    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help="Fetch Wikipedia content for all Topics that have Wikipedia pages"
        ),
    )

    def handle(self, *args, **options):
        if options['all']:
            success = Topic.objects.fetch_wikipedia_texts(topic_ids='all')
        elif len(args) == 0:
            raise CommandError("Specify topic_id(s) or --all topics.")
        else:
            ids = [int(s) for s in args[0].split(' ')]
            success = Topic.objects.fetch_wikipedia_texts(topic_ids=ids)

        verbosity = int(options['verbosity'])

        if success:
            if verbosity > 0:
                self.stdout.write('Done')
        else:
            self.stderr.write("Error when fetching Wikipedia texts")




