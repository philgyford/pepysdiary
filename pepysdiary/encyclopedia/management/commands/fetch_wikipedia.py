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
        args_error_message = "Specify topic_id(s) or --all topics."
        number_updated = 0

        if options['all']:
            success = Topic.objects.fetch_wikipedia_texts(topic_ids='all')
        elif len(args) == 0:
            raise CommandError(args_error_message)
        else:
            try:
                ids = [int(s) for s in args[0].split(' ')]
            except ValueError:
                raise CommandError(args_error_message)
            number_updated = Topic.objects.fetch_wikipedia_texts(topic_ids=ids)

        verbosity = int(options['verbosity'])

        if number_updated > 0:
            if verbosity > 0:
                self.stdout.write('Done')
        else:
            self.stderr.write("No topics were updated with Wikipedia texts.")




