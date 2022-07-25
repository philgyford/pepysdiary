# -*- coding: utf-8 -*-


from django.db import migrations, models

import pepysdiary.common.models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DayEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("event_date", models.DateField(db_index=True)),
                ("url", models.URLField(max_length=255, blank=True)),
                (
                    "source",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (10, "John Gadbury\u2019s London Diary"),
                            (20, "In Parliament"),
                            (30, "In Earl\u2019s Colne, Essex"),
                        ],
                    ),
                ),
            ],
            options={"ordering": ["event_date"], "verbose_name": "Day Event"},
            bases=(models.Model, pepysdiary.common.models.OldDateMixin),
        ),
    ]
