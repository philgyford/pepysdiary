from django import forms

from pepysdiary.encyclopedia.models import Category


class CategoryMapForm(forms.Form):
    """
    The form on the map that shows Topics in a particular category.
    We just have one select field showing a list of available categories.
    """
    category = forms.ChoiceField(required=True,
                            widget=forms.Select(attrs={'class': 'form-control'}),
                            choices=Category.objects.map_category_choices())

    def clean_category(self):
        category = self.cleaned_data['category']
        if int(category) not in Category.objects.valid_map_category_ids():
            raise forms.ValidationError("'%s' is not a valid category ID" %
                                                                    category)
        return category
