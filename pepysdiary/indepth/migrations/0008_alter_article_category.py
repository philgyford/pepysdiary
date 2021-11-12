# Generated by Django 3.2.6 on 2021-11-05 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("indepth", "0007_alter_article_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="category",
            field=models.CharField(
                choices=[
                    ("book-reviews", "Book Reviews"),
                    ("background", "In-depth Background"),
                    ("misc", "Miscellaneous"),
                ],
                db_index=True,
                default="misc",
                max_length=25,
            ),
        ),
    ]