# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0001_initial'),
        ('encyclopedia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='letter_references',
            field=models.ManyToManyField(related_name='topics', to='letters.Letter'),
            preserve_default=True,
        ),
    ]
