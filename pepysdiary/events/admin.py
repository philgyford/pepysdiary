from django.contrib import admin

from pepysdiary.common.admin import YearmonthListFilter
from pepysdiary.events.models import DayEvent


class EventDateYearmonthListFilter(YearmonthListFilter):
    filter_field = "event_date"


class DayEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_date",
        "source",
        "title",
    )
    list_filter = ("source", EventDateYearmonthListFilter)
    search_fields = [
        "title",
    ]
    readonly_fields = (
        "date_created",
        "date_modified",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "source",
                    "event_date",
                    "title",
                    "url",
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    "date_created",
                    "date_modified",
                )
            },
        ),
    )


admin.site.register(DayEvent, DayEventAdmin)
