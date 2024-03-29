# Generated by Django 3.0.4 on 2020-03-31 16:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("indepth", "0004_popular_article_search_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="author",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text="Optional.",
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="indepth_articles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
