from optparse import make_option
import re

from django.core.management.base import BaseCommand, CommandError

from pepysdiary.annotations.models import Annotation
from pepysdiary.membership.models import Person


class Command(BaseCommand):
    args = '[options] <email> <person_id>'
    help = 'Associate Annotations by a particular email address to a '\
                                                        'particular Person.'
    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
            action='store_true',
            dest='dry-run',
            default=False,
            help="Output what would have happened, but don't change the "\
                                                                "database."),
        )

    email = None
    person = None
    dry_run = False

    def handle(self, *args, **options):
        self.process_args(args, options)

        annotations = Annotation.objects.filter(
                                            user_email=self.email, user=None)
        if annotations.count() == 0:
            raise CommandError("There are no Annotations (without a Person "
                "already) associated with the email address %s" % self.email)

        if self.dry_run == False:
            updated = annotations.update(user=self.person)

            # Set the person's first_comment_date.
            first_comment = Annotation.visible_objects.filter(
                                user=self.person).order_by('submit_date')[0]
            first_comment_date = first_comment.submit_date
            self.person.first_comment_date = first_comment_date
            self.person.save()

        else:
            print("DRY RUN, NOTHING CHANGED IN THE DATABASE. "\
                    "WHAT WOULD HAVE HAPPENED:")
            updated = annotations.count()
            first_comment = Annotation.visible_objects.filter(
                                    user_email=self.email, user=None).order_by(
                                    'submit_date')[0]
            first_comment_date = first_comment.submit_date

        if updated == 1:
            output_str = "1 Annotation was"
        else:
            output_str = "%s Annotations were" % updated

        print("%s associated with %s (ID %s)." % (
                    output_str, self.person.get_full_name(), self.person.id))
        print("%s first_comment_date was set to %s" % (
                            self.person.get_full_name(), first_comment_date))

    def process_args(self, args, options):
        if len(args) != 2:
            raise CommandError("Please suppy an email address and Person ID.")

        # Very loose test for email address format:
        if re.match('^.*?@.*?\..*?$', args[0]) is None:
            raise CommandError("The supplied email address (%s) doesn't look "
                "anything like an email address." % args[0])
        else:
            self.email = args[0]

        try:
            self.person = Person.objects.get(pk=int(args[1]))
        except Person.DoesNotExist:
            raise CommandError("There is no Person with an ID of '%s'" %
                                                                    args[1])

        if options.get('dry-run'):
            self.dry_run = True
