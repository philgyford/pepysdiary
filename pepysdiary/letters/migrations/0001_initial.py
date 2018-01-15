# -*- coding: utf-8 -*-


from django.db import models, migrations
import pepysdiary.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('encyclopedia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text=b'eg, "Thomas Hill to Samuel Pepys".', max_length=100)),
                ('letter_date', models.DateField()),
                ('display_date', models.CharField(help_text=b'eg "Thursday 27 April 1665". Because days of the week are calculated wrong for old dates.', max_length=50)),
                ('text', models.TextField()),
                ('footnotes', models.TextField(blank=True)),
                ('excerpt', models.TextField(help_text=b'200 or so characters from the start of the letter, after salutations.')),
                ('source', models.IntegerField(blank=True, null=True, choices=[(10, b'Guy de la B\xc3\xa9doy\xc3\xa8re'), (20, b'Helen Truesdell Heath')])),
                ('slug', models.SlugField(unique_for_date=b'letter_date')),
                ('comment_count', models.IntegerField(default=0)),
                ('last_comment_time', models.DateTimeField(null=True, blank=True)),
                ('allow_comments', models.BooleanField(default=True)),
                ('recipient', models.ForeignKey(related_name='letter_recipients', to='encyclopedia.Topic', on_delete=models.SET_NULL)),
                ('sender', models.ForeignKey(related_name='leter_senders', to='encyclopedia.Topic', on_delete=models.SET_NULL)),
            ],
            options={
                'ordering': ['letter_date'],
            },
            bases=(models.Model, pepysdiary.common.models.OldDateMixin),
        ),
    ]
