# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("encyclopedia", "0002_topic_letter_references"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="wikipedia_html",
            field=models.TextField(
                help_text=b"Will be populated automatically.", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="topic",
            name="wikipedia_last_udpate",
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
