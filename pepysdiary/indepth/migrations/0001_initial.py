# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('intro', models.TextField(help_text=b'Can use Markdown.')),
                ('intro_html', models.TextField(help_text=b'The intro field, with Markdown etc, turned into HTML.', blank=True)),
                ('text', models.TextField(help_text=b'Can use Markdown. Any images should be put in `pepysdiary/indepth/static/img/indepth/`.', blank=True)),
                ('text_html', models.TextField(help_text=b'The text field, with Markdown etc, turned into HTML.', blank=True)),
                ('excerpt', models.TextField(blank=True)),
                ('date_published', models.DateTimeField(null=True, blank=True)),
                ('slug', models.SlugField(unique_for_date=b'date_published')),
                ('comment_count', models.IntegerField(default=0)),
                ('last_comment_time', models.DateTimeField(null=True, blank=True)),
                ('allow_comments', models.BooleanField(default=True)),
                ('status', models.IntegerField(default=10, choices=[(10, b'Draft'), (20, b'Published')])),
            ],
            options={
                'ordering': ['-date_published'],
            },
            bases=(models.Model,),
        ),
    ]
