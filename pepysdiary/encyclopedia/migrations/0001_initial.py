# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('topic_count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('order_title', models.CharField(max_length=255, blank=True)),
                ('summary', models.TextField(help_text=b'Can use Markdown.', blank=True)),
                ('summary_html', models.TextField(help_text=b'The summary field, with Markdown etc, turned into HTML.', blank=True)),
                ('wheatley', models.TextField(help_text=b'Can use Markdown. Taken from footnotes in the 1893 Wheatley edition of the diary.', blank=True)),
                ('wheatley_html', models.TextField(help_text=b'The wheatley field, with Markdown etc, turned into HTML.', blank=True)),
                ('tooltip_text', models.TextField(help_text=b'For hovering over links in diary entries.', blank=True)),
                ('wikipedia_fragment', models.CharField(help_text=b"From the Wikipedia page URL, if any, eg, 'Samuel_Pepys'.", max_length=255, blank=True)),
                ('thumbnail', models.ImageField(help_text=b'100 x 120 pixels', null=True, upload_to=b'encyclopedia/thumbnails', blank=True)),
                ('on_pepys_family_tree', models.BooleanField(default=False, verbose_name=b'Is on the Pepys family tree?')),
                ('comment_count', models.IntegerField(default=0)),
                ('last_comment_time', models.DateTimeField(null=True, blank=True)),
                ('allow_comments', models.BooleanField(default=True)),
                ('map_category', models.CharField(blank=True, help_text=b'(UNUSED?) The type of object this is on maps', max_length=20, db_index=True, choices=[(b'area', b'Area'), (b'gate', b'Gate'), (b'home', b"Pepys' home(s)"), (b'misc', b'Misc'), (b'road', b'Road/Street'), (b'stair', b'Stair/Pier'), (b'town', b'Town/Village')])),
                ('latitude', models.DecimalField(null=True, max_digits=11, decimal_places=6, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=11, decimal_places=6, blank=True)),
                ('zoom', models.SmallIntegerField(null=True, blank=True)),
                ('shape', models.TextField(help_text=b"Lat/long coordinate pairs, separated by semicolons, eg '51.513558,-0.104268;51.513552,-0.104518;...', from http://www.birdtheme.org/useful/v3largemap.html (formatted slightly differently).", blank=True)),
                ('categories', models.ManyToManyField(related_name='topics', to='encyclopedia.Category')),
                ('diary_references', models.ManyToManyField(related_name='topics', to='diary.Entry')),
            ],
            options={
                'ordering': ['order_title'],
            },
            bases=(models.Model,),
        ),
    ]
