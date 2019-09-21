import re

from django.db import migrations


def fix_josselin_links(apps, schema_editor):
    """
    Change the Josselin's diary links from being like
        http://linux02.lib.cam.ac.uk/earlscolne/diary/70016080.htm
    to
        https://wwwe.lib.cam.ac.uk/earls_colne/diary/70016080.htm
    """
    DayEvent = apps.get_model("events", "DayEvent")

    # Can't access DayEvent.JOSSELIN_CHOICE in the migration, so having
    # to hard-code the value 30 here:
    for event in DayEvent.objects.filter(source=30):
        g = re.search(r"diary\/(.*?)$", event.url)
        if g:
            event.url = "https://wwwe.lib.cam.ac.uk/earls_colne/diary/{}".format(
                g.groups()[0]
            )
            event.save()


class Migration(migrations.Migration):

    dependencies = [("events", "0001_initial")]

    operations = [
        migrations.RunPython(fix_josselin_links, reverse_code=migrations.RunPython.noop)
    ]
