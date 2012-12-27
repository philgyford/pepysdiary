from django.contrib import admin

from pepysdiary.indepth.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'date_published', 'comment_count', )
    search_fields = ['title', 'intro', 'text', ]
    readonly_fields = ('date_created', 'date_modified', )
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status', 'date_published', )
        }),
        (None, {
            'fields': ('intro', 'text', 'excerpt', )
        }),
        (None, {
            'fields': ('comment_count', 'date_created', 'date_modified', )
        }),
    )

admin.site.register(Article, ArticleAdmin)
