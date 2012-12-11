from django.contrib import admin

from pepysdiary.encyclopedia.models import Topic


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
