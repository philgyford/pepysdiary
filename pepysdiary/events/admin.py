from django.contrib import admin

from pepysdiary.events.models import DayEvent


class DayEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_date",
        "source",
        "title",
    )
    search_fields = [
        "title",
    ]
    readonly_fields = (
        "date_created",
        "date_modified",
    )
    fieldsets = (
        (None, {"fields": ("source", "event_date", "title", "url",)}),
        (None, {"fields": ("date_created", "date_modified",)}),
    )


admin.site.register(DayEvent, DayEventAdmin)
