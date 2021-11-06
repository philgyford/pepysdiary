from django.contrib import admin
from django.utils.html import format_html

from pepysdiary.indepth.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "item_authors",
        "status",
        "category",
        "date_published",
        "comment_count",
    )
    list_editable = ("category",)
    search_fields = [
        "title",
        "intro",
        "text",
    ]
    readonly_fields = (
        "date_created",
        "date_modified",
        "last_comment_time",
        "cover_dimensions",
        "cover_preview",
    )
    raw_id_fields = ("author",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "status",
                    "date_published",
                    "category",
                    "author",
                    "author_name",
                    "author_url",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "cover",
                    ("cover_preview", "cover_dimensions"),
                    "item_authors",
                    "intro",
                    "text",
                    "excerpt",
                )
            },
        ),
        (
            "Comments and times",
            {
                "fields": (
                    "date_created",
                    "date_modified",
                    "allow_comments",
                    "comment_count",
                    "last_comment_time",
                ),
            },
        ),
    )

    @admin.display()
    def cover_dimensions(self, obj):
        if obj.cover_width == 0 and obj.cover_height == 0:
            return "–"
        else:
            return f"{obj.cover_width} × {obj.cover_height}"

    @admin.display()
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" width="{}" height="{}" alt="The cover">',
                obj.cover.url,
                round(obj.cover_width / 2),
                round(obj.cover_height / 2),
            )
        else:
            return "–"


admin.site.register(Article, ArticleAdmin)
