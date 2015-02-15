# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pepysdiary.common.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('diary_date', models.DateField(unique=True)),
                ('text', models.TextField(help_text=b'HTML only, no Markdown.')),
                ('footnotes', models.TextField(help_text=b'HTML only, no Markdown.', blank=True)),
                ('comment_count', models.IntegerField(default=0)),
                ('last_comment_time', models.DateTimeField(null=True, blank=True)),
                ('allow_comments', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['diary_date'],
                'verbose_name_plural': 'Entries',
            },
            bases=(models.Model, pepysdiary.common.models.OldDateMixin),
        ),
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('text', models.TextField(help_text=b'Can use Markdown.')),
                ('text_html', models.TextField(help_text=b'The text field, with Markdown etc, turned into HTML.')),
                ('summary_date', models.DateField(help_text=b'Only the month and year are relevant.')),
            ],
            options={
                'ordering': ['summary_date'],
                'verbose_name_plural': 'Summaries',
            },
            bases=(models.Model, pepysdiary.common.models.OldDateMixin),
        ),
    ]
