# Generated by Django 2.1.7 on 2019-03-23 17:37

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("encyclopedia", "0005_auto_20180115_1635"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="search_document",
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
    ]
