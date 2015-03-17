# coding: utf-8
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from pepysdiary.encyclopedia.models import Topic


class Command(BaseCommand):
    args = '<topic_id topic_id ...>'
    help = "Fetches Wikipedia content Topics that have it"

    option_list = BaseCommand.option_list + (
        make_option('-a', '--all',
            action='store_true',
            dest='all',
            default=False,
            help="Fetch Wikipedia content for all Topics that have Wikipedia pages."
        ),
        make_option('-n', '--num',
            action='store',
            dest='num',
            default=False,
            type='int',
            help="Fetch Wikipedia content for this many Topics, starting with those whose fetched content is oldest."
        ),
    )

    def handle(self, *args, **options):
        args_error_message = "Specify topic_id(s), --all topics or --num=n topics."

        if options['all']:
            number_updated = Topic.objects.fetch_wikipedia_texts(num='all')
        elif options['num']:
            number_updated = Topic.objects.fetch_wikipedia_texts(num=options['num'])
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
                self.stdout.write('Fetched %s topic(s)' % number_updated)
        else:
            self.stderr.write("No topics were updated with Wikipedia texts.")




