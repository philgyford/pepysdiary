# Generated by Django 2.0.1 on 2018-01-15 16:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.CharField(
                choices=[
                    ("events", "Events"),
                    ("housekeeping", "Housekeeping"),
                    ("new-features", "New features"),
                    ("pepys-in-the-media", "Pepys in the media"),
                    ("press", "Press for this site"),
                    ("statistics", "Site statistics"),
                ],
                db_index=True,
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="intro",
            field=models.TextField(help_text="Can use Markdown."),
        ),
        migrations.AlterField(
            model_name="post",
            name="intro_html",
            field=models.TextField(
                blank=True,
                help_text="The intro field, with Markdown etc, turned into HTML.",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="status",
            field=models.IntegerField(
                choices=[(10, "Draft"), (20, "Published")], default=10
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="text",
            field=models.TextField(
                blank=True,
                help_text="Can use Markdown. Images go in `pepysdiary/news/static/img/news/`. Files go in `pepysdiary/news/static/files/news/`",  # noqa: E501
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="text_html",
            field=models.TextField(
                blank=True,
                help_text="The text field, with Markdown etc, turned into HTML.",
            ),
        ),
    ]
