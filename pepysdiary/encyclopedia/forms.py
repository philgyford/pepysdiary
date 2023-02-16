from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from .fields import CategoryMultipleChoiceField
from .models import Category, Topic


class CategoryMapForm(forms.Form):
    """
    The form on the map that shows Topics in a particular category.
    We just have one select field showing a list of available categories.
    """

    category = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        choices=Category.objects.map_category_choices(),
    )


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        exclude = ()

    categories = CategoryMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("categories", is_stacked=False),
    )
