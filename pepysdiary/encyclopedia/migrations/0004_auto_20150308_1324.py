# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('encyclopedia', '0003_auto_20150308_1322'),
    ]

    operations = [
        migrations.RenameField(
            model_name='topic',
            old_name='wikipedia_last_udpate',
            new_name='wikipedia_last_fetch',
        ),
    ]
