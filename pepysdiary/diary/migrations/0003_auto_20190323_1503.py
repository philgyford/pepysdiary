# Generated by Django 2.1.7 on 2019-03-23 15:03

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0002_auto_20180115_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='search_document',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='entry',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='diary_entry_search__7a3c43_gin'),
        ),
    ]