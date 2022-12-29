from django.db import migrations
from django.db.models import Q

# To replace "L&M" in diary Entry text and footnotes with "L&amp;M"
# because I stupidly entered them wrong.


def forwards(apps, schema_editor):
    Entry = apps.get_model("diary", "Entry")

    for entry in Entry.objects.filter(
        Q(text__contains="L&M") | Q(footnotes__contains="L&M")
    ):
        entry.text = entry.text.replace("L&M", "L&amp;M")
        entry.footnotes = entry.footnotes.replace("L&M", "L&amp;M")
        entry.save()


def backwards(apps, schema_editor):
    Entry = apps.get_model("diary", "Entry")

    for entry in Entry.objects.filter(
        Q(text__contains="L&amp;M") | Q(footnotes__contains="L&amp;M")
    ):
        entry.text = entry.text.replace("L&amp;M", "L&M")
        entry.footnotes = entry.footnotes.replace("L&amp;M", "L&M")
        entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ("diary", "0004_populate_entry_search_index"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
