from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .forms import TopicForm
from .models import Category, Topic


class TopicAdmin(admin.ModelAdmin):
    form = TopicForm

    list_display = (
        "id",
        "title",
        "comment_count",
        "wikipedia_last_fetch",
    )
    list_display_links = ("title",)
    filter_horizontal = ("categories",)
    search_fields = [
        "title",
    ]
    readonly_fields = (
        "date_created",
        "date_modified",
        "order_title",
        "last_comment_time",
    )
    raw_id_fields = ("summary_author",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "order_title",
                    "categories",
                    "summary",
                    "wheatley",
                    "tooltip_text",
                    "wikipedia_fragment",
                    "allow_comments",
                ),
            },
        ),
        (
            "People",
            {
                "fields": (
                    "thumbnail",
                    "on_pepys_family_tree",
                )
            },
        ),
        (
            "Places",
            {
                "fields": (
                    "map_category",
                    "latitude",
                    "longitude",
                    "zoom",
                    "shape",
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    "date_created",
                    "date_modified",
                    "summary_author",
                    "summary_publication_date",
                    "comment_count",
                    "last_comment_time",
                    "wikipedia_last_fetch",
                ),
            },
        ),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # If we were creating it for the first time, the order_title won't
        # have been made, so we need to save it again.
        form.instance.save()


admin.site.register(Topic, TopicAdmin)


class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)

    prepopulated_fields = {
        "slug": ("title",),
    }


admin.site.register(Category, CategoryAdmin)
