from django.contrib import admin

from pepysdiary.letters.models import Letter


class LetterAdmin(admin.ModelAdmin):
    list_display = ('letter_date', 'title', 'comment_count', )
    search_fields = ('title', 'text', 'footnotes', 'excerpt', )
    readonly_fields = ('date_created', 'date_modified', 'last_comment_time', )
    raw_id_fields = ('sender', 'recipient', )
    fieldsets = (
        (None, {
            'fields': ('title', 'letter_date', 'display_date',
                        'sender', 'recipient',
                        'slug', 'source', 'allow_comments', )
        }),
        (None, {
            'fields': ('text', 'footnotes', 'excerpt', )
        }),
        (None, {
            'fields': ('date_created', 'date_modified', 'comment_count',
                                                        'last_comment_time', ),
        }),
    )

admin.site.register(Letter, LetterAdmin)
