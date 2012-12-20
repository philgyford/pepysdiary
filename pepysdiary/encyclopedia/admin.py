from django.contrib import admin

from treebeard.admin import TreeAdmin

from pepysdiary.encyclopedia.models import Category, Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'comment_count', )
    readonly_fields = ('date_created', 'date_modified', 'order_title', )
    fieldsets = (
        (None, {
            'fields': ('title', 'order_title', 'summary', 'wheatley',
                        'tooltip_text', 'wikipedia_fragment',
                        'date_created', 'date_modified', ),
        }),
        ('People', {
            'fields': ('thumbnail', )
        }),
        ('Places', {
            'fields': ('map_category', 'latitude', 'longitude', 'zoom',
                        'shape', )
        }),
    )

admin.site.register(Topic, TopicAdmin)


class CategoryAdmin(TreeAdmin):
    prepopulated_fields = {"slug": ("title", ), }

admin.site.register(Category, CategoryAdmin)
