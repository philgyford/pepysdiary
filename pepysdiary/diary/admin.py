from django.contrib import admin

from pepysdiary.diary.models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'diary_date', 'comment_count', )
    readonly_fields = ('date_created', 'date_modified', 'last_comment_time', )
    search_fields = ['title', ]

    search_fields = ['title', 'text', 'footnotes', ]
    fieldsets = (
        (None, {
            'fields': ('title', 'diary_date', 'text', 'footnotes', ),
        }),
        (None, {
            'fields': ('date_created', 'date_modified', 'comment_count',
                                                        'last_comment_time', ),
        }),
    )

admin.site.register(Entry, EntryAdmin)
