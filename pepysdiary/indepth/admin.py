from django.contrib import admin
from django.utils.html import format_html

from pepysdiary.indepth.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "item_authors",
        "status_icon",
        "category",
        "date_published",
        "comment_count",
    )
    list_filter = ("category",)
    search_fields = [
        "title",
        "intro",
        "text",
        "excerpt",
        "item_author",
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
        if obj.cover_width and obj.cover_height:
            return f"{obj.cover_width} × {obj.cover_height}"
        else:
            return "–"

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

    def status_icon(self, obj):
        if obj.status == Article.Status.PUBLISHED:
            return "✅"
        elif obj.status == Article.Status.DRAFT:
            return "…"
        else:
            return ""

    status_icon.short_description = "Status"


admin.site.register(Article, ArticleAdmin)
