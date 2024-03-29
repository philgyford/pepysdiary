# Generated by Django 4.1.6 on 2023-02-14 16:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0002_fix_josselin_links_20190921_1456"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dayevent",
            name="source",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (10, "John Gadbury’s London Diary"),
                    (20, "In Parliament"),
                    (30, "In Earl’s Colne, Essex"),
                    (40, "Times"),
                ],
                null=True,
            ),
        ),
    ]
