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
        fields = (
            "title",
            "order_title",
            "summary",
            "summary_author",
            "summary_publication_date",
            "wheatley",
            "tooltip_text",
            "wikipedia_fragment",
            "thumbnail",
            "on_pepys_family_tree",
            "allow_comments",
            "map_category",
            "latitude",
            "longitude",
            "zoom",
            "shape",
            "categories",
        )

    categories = CategoryMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("categories", is_stacked=False),
    )
