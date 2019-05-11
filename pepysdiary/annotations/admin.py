from django.contrib import admin
from django_comments import get_model
from django_comments.admin import CommentsAdmin
from django_comments.models import CommentFlag

from pepysdiary.annotations.models import Annotation


class CommentFlagInline(admin.TabularInline):
    model = CommentFlag
    extra = 0
    raw_id_fields = ("user",)


class AnnotationsAdmin(CommentsAdmin):
    inlines = [CommentFlagInline]

    def flag(self, obj):
        flag_name = ""
        try:
            flag_name = list(obj.flags.values())[0]["flag"]
        except IndexError:
            pass
        return flag_name

    list_display = (
        "name",
        "content_type",
        "object_pk",
        "ip_address",
        "submit_date",
        "flag",
        "is_public",
        "is_removed",
    )
    list_filter = ("submit_date", "site", "is_public", "is_removed", "flags__flag")


if get_model() is Annotation:
    admin.site.register(Annotation, AnnotationsAdmin)
