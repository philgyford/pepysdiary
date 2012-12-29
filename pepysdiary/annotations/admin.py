from django.contrib import admin
from django.contrib.comments import get_model
from django.contrib.comments.admin import CommentsAdmin

from pepysdiary.annotations.models import Annotation


class AnnotationsAdmin(CommentsAdmin):
    pass


if get_model() is Annotation:
    admin.site.register(Annotation, AnnotationsAdmin)
