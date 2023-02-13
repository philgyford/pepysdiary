import calendar
import re
from datetime import date

from django.contrib import admin

from pepysdiary.common.models import Config
from pepysdiary.diary.models import Entry


class YearmonthListFilter(admin.SimpleListFilter):
    """
    Parent class for Admin classes that want to have a list_filter that
    filters by a model's DateTimeField with separate links for each
    month.

    Child classes should inherit this, and define the filter_field
    property. Then use it like:

    list_filter(ChildYearmonthListFilter,)
    """

    # The DateTimeField on the model that we're filtering. e.g. diary_date.
    # Child classes must define this.
    filter_field = None

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Month"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "yearmonth"

    def __init__(self, *args, **kwargs):
        if self.filter_field is None:
            raise NotImplementedError(
                "Child classes of YearmonthListFilter must define the "
                "'filter_field' property."
            )

        return super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        years_months = Entry.objects.all_years_months()

        choices = []
        for y, months in years_months:
            for m_count, m in enumerate(months):
                choices.append(
                    (
                        # Will be like ('1660-03', 'Mar 1660'):
                        "%s-%02d" % (y, (m_count + 1)),
                        "%s %s" % (y, m),
                    )
                )

        return choices

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # self.value() should be of the form '1660-01'.
        if (
            self.value() is not None
            and re.match(r"^\d{,4}-\d{,2}$", self.value()) is not None
        ):
            [year, month] = [int(n) for n in self.value().split("-")]
            last_day = calendar.monthrange(year, month)[1]

            kwargs = {
                f"{self.filter_field}__gte": date(year, month, 1),
                f"{self.filter_field}__lte": date(year, month, last_day),
            }

            return queryset.filter(**kwargs)


class ConfigAdmin(admin.ModelAdmin):
    list_display = ("site", "allow_registration", "allow_login", "allow_comments")
    readonly_fields = ("date_created", "date_modified")
    fieldsets = (
        (None, {"fields": ("site",)}),
        (
            "Allowed actions",
            {"fields": ("allow_registration", "allow_login", "allow_comments")},
        ),
        (
            "Registration",
            {
                "fields": (
                    "use_registration_captcha",
                    "use_registration_question",
                    "registration_question",
                    "registration_answer",
                )
            },
        ),
    )


admin.site.register(Config, ConfigAdmin)
