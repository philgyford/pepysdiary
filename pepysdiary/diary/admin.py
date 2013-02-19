import calendar
from datetime import date
import re

from django.contrib import admin

from pepysdiary.diary.models import Entry, Summary


class YearmonthListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Month'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'yearmonth'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        years = (1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, )
        months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                                                        'Oct', 'Nov', 'Dec', )
        choices = []
        for y in years:
            for (m_count, m) in enumerate(months):
                if y == 1669 and m_count > 4:
                    # Nothing after May 1669.
                    continue
                choices.append((
                    # Will be like ('1660-03', 'Mar 1660'):
                    '%s-%02d' % (y, (m_count + 1)),
                    '%s %s' % (y, m),
                ))
        return choices

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # self.value() should be of the form '1660-01'.
        if self.value() is not None and \
            re.match(r'^\d{,4}-\d{,2}$', self.value()) is not None:

            [year, month] = [int(n) for n in self.value().split('-')]
            last_day = calendar.monthrange(year, month)[1]

            return queryset.filter(diary_date__gte=date(year, month, 1),
                                diary_date__lte=date(year, month, last_day))


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'diary_date', 'comment_count', )
    list_filter = (YearmonthListFilter, )
    search_fields = ['title', 'text', 'footnotes', ]
    readonly_fields = ('date_created', 'date_modified', 'last_comment_time', )
    fieldsets = (
        (None, {
            'fields': ('title', 'diary_date', 'text', 'footnotes',
                                                        'allow_comments', ),
        }),
        (None, {
            'fields': ('date_created', 'date_modified', 'comment_count',
                                                        'last_comment_time', ),
        }),
    )

admin.site.register(Entry, EntryAdmin)


class SummaryAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ['title', 'text', ]
    readonly_fields = ('date_created', 'date_modified', )
    fieldsets = (
        (None, {
            'fields': ('title', 'summary_date', 'text', ),
        }),
        (None, {
            'fields': ('date_created', 'date_modified', ),
        }),
    )

admin.site.register(Summary, SummaryAdmin)
