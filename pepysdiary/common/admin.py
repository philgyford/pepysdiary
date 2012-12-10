from django.contrib import admin

from pepysdiary.common.models import Config


class ConfigAdmin(admin.ModelAdmin):
    list_display = ('site', 'allow_registration', 'allow_login',
                    'allow_comments', )
    readonly_fields = ('date_created', 'date_modified', )

admin.site.register(Config, ConfigAdmin)
