from django.contrib import admin

from treebeard.admin import TreeAdmin

from pepysdiary.encyclopedia.models import Category, Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'comment_count', )
    readonly_fields = ('date_created', 'date_modified', 'order_title', )
    filter_horizontal = ('categories', )
    fieldsets = (
        (None, {
            'fields': ('title', 'order_title', 'categories',
                        'summary', 'wheatley',
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

    def save_related(self, request, form, formsets, change):
        super(TopicAdmin, self).save_related(request, form, formsets, change)
        # If we were creating it for the first time, the order_title won't
        # have been made, so we need to save it again.
        form.instance.save()


admin.site.register(Topic, TopicAdmin)


class CategoryAdmin(TreeAdmin):
    prepopulated_fields = {"slug": ("title", ), }

admin.site.register(Category, CategoryAdmin)
