from django.contrib import admin

from pepysdiary.news.models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'date_published',
                                                            'comment_count', )
    search_fields = ['title', 'intro', 'text', ]
    readonly_fields = ('date_created', 'date_modified', )
    fieldsets = (
        (None, {
            'fields': ('title', 'status', 'date_published', )
        }),
        (None, {
            'fields': ('category', 'intro', 'text', )
        }),
        (None, {
            'fields': ('comment_count', 'date_created', 'date_modified', )
        }),
    )

admin.site.register(Post, PostAdmin)
