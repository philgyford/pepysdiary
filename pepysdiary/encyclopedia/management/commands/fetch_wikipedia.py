from django.core.management.base import BaseCommand, CommandError

from pepysdiary.encyclopedia.models import Topic


class Command(BaseCommand):
    """
    Fetches Wikipedia HTML for Topics.

    Gets it for all Topics:
    ./manage.py fetch_wikipedia --all

    Gets it for the three topics with these IDs:
    ./manage.py fetch_wikipedia --ids 150 112 344

    Gets it for the 20 Topics that have been fetched least recently:
    ./manage.py fetch_wikipedia --num=20

    Add verbosity with:
    ./manage.py fetch_wikipedia --num=20 --verbosity=2

    0: No output
    1: The number of successes and failures
    2: Lists all IDs which succeeded and which failed.
    """

    help = (
        "Fetches Wikipedia content for Topics that have it. "
        "Use --ids OR --all OR --num."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            "-a",
            action="store_true",
            dest="all",
            default=False,
            help="Fetch Wikipedia content for all Topics that have Wikipedia pages.",
        )
        parser.add_argument(
            "--num",
            "-n",
            action="store",
            dest="num",
            default=False,
            type=int,
            help="Fetch Wikipedia content for this many Topics, starting with those "
            "whose fetched content is oldest.",
        )
        parser.add_argument(
            "--ids",
            "-i",
            action="store",
            nargs="+",
            type=int,
            help="Space-separated ID(s). Only fetch Wikipedia content for Topics "
            "with these id(s)",
        )

    def handle(self, *args, **options):
        args_error_message = "Specify --ids, --all topics or --num=n topics."

        if options["all"]:
            updated = Topic.objects.fetch_wikipedia_texts(num="all")
        elif options["num"]:
            updated = Topic.objects.fetch_wikipedia_texts(num=options["num"])
        elif options["ids"]:
            updated = Topic.objects.fetch_wikipedia_texts(topic_ids=options["ids"])
        else:
            raise CommandError(args_error_message)

        verbosity = int(options["verbosity"])

        if verbosity > 0:
            num_topics = len(updated["success"])
            self.stdout.write(f"Successfully fetched {num_topics} topic(s)")
            if verbosity > 1:
                ids = ", ".join(str(id) for id in updated["success"])
                self.stdout.write(f"IDs: {ids}")

            if len(updated["failure"]) > 0:
                num_topics = len(updated["failure"])
                self.stderr.write(
                    f"Tried and failed to fetch texts for {num_topics} topic(s)"
                )
                if verbosity > 1:
                    ids = ", ".join(str(id) for id in updated["failure"])
                    self.stderr.write(f"IDs: {ids}")
