from django.contrib import admin

from pepysdiary.news.models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "category",
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
        (None, {"fields": ("title", "status", "date_published", "allow_comments",)}),
        (None, {"fields": ("category", "intro", "text",)}),
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


admin.site.register(Post, PostAdmin)
