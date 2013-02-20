from django.contrib import admin

from pepysdiary.common.models import Config


class ConfigAdmin(admin.ModelAdmin):
    list_display = ('site', 'allow_registration', 'allow_login',
                    'allow_comments', )
    readonly_fields = ('date_created', 'date_modified', )
    fieldsets = (
        (None, {
            'fields': ('site', )
        }),
        ('Allowed actions', {
            'fields': ('allow_registration', 'allow_login', 'allow_comments', )
        }),
        ('Registration', {
            'fields': ('use_registration_captcha', 'use_registration_question',
                        'registration_question', 'registration_answer', )
        }),
    )

admin.site.register(Config, ConfigAdmin)
