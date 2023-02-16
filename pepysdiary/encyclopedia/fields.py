from django import forms
from django.utils.html import mark_safe


class CategoryChoiceField(forms.ModelChoiceField):
    """
    Indents the option texts to represent the hierarchy.
    """

    def label_from_instance(self, obj):
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" * (obj.depth - 2)
        if obj.depth > 1:
            indent += "└─&nbsp;&nbsp;"
        return mark_safe(f"{indent}{obj.title}")


class CategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Indents the option texts to represent the hierarchy.
    """

    def label_from_instance(self, obj):
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" * (obj.depth - 2)
        if obj.depth > 1:
            indent += "└─&nbsp;&nbsp;"
        return mark_safe(f"{indent}{obj.title}")
