from django.contrib import admin

from pepysdiary.indepth.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "date_published",
        "comment_count",
    )
    search_fields = [
        "title",
        "intro",
        "text",
    ]
    readonly_fields = (
        "date_created",
        "date_modified",
        "last_comment_time",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "status",
                    "date_published",
                    "allow_comments",
                )
            },
        ),
        (None, {"fields": ("intro", "text", "excerpt",)}),
        (
            None,
            {
                "fields": (
                    "date_created",
                    "date_modified",
                    "comment_count",
                    "last_comment_time",
                ),
            },
        ),
    )


admin.site.register(Article, ArticleAdmin)
