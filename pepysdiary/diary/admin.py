from django.contrib import admin

from pepysdiary.diary.models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'diary_date', 'comment_count', )
    readonly_fields = ('date_created', 'date_modified', )
    search_fields = ['title', ]

admin.site.register(Entry, EntryAdmin)
