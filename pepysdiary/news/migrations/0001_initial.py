# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('intro', models.TextField(help_text=b'Can use Markdown.')),
                ('intro_html', models.TextField(help_text=b'The intro field, with Markdown etc, turned into HTML.', blank=True)),
                ('text', models.TextField(help_text=b'Can use Markdown. Images go in `pepysdiary/news/static/img/news/`. Files go in `pepysdiary/news/static/files/news/`', blank=True)),
                ('text_html', models.TextField(help_text=b'The text field, with Markdown etc, turned into HTML.', blank=True)),
                ('date_published', models.DateTimeField(null=True, blank=True)),
                ('comment_count', models.IntegerField(default=0)),
                ('last_comment_time', models.DateTimeField(null=True, blank=True)),
                ('allow_comments', models.BooleanField(default=True)),
                ('status', models.IntegerField(default=10, choices=[(10, b'Draft'), (20, b'Published')])),
                ('category', models.CharField(db_index=True, max_length=25, choices=[(b'events', b'Events'), (b'housekeeping', b'Housekeeping'), (b'new-features', b'New features'), (b'pepys-in-the-media', b'Pepys in the media'), (b'press', b'Press for this site'), (b'statistics', b'Site statistics')])),
            ],
            options={
                'ordering': ['-date_published'],
            },
            bases=(models.Model,),
        ),
    ]
