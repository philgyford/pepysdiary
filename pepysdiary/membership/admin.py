from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from pepysdiary.membership.models import Person
from pepysdiary.membership.utilities import validate_person_name


class PersonCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    name = forms.CharField(max_length=50, validators=[validate_person_name],
        help_text="Required. 50 characters or fewer. Spaces allowed.")
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                                widget=forms.PasswordInput)

    class Meta:
        model = Person
        fields = ('email', 'name')

    def clean_name(self):
        # Since Person.name is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        name = self.cleaned_data['name']
        try:
            Person.objects.get(name=name)
        except Person.DoesNotExist:
            return name
        raise forms.ValidationError("A user with that name already exists.")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        person = super(PersonCreationForm, self).save(commit=False)
        person.set_password(self.cleaned_data["password1"])
        if commit:
            person.save()
        return person


class PersonChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Person

    def __init__(self, *args, **kwargs):
        super(PersonChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class PersonAdmin(UserAdmin):
    # The forms to add and change user instances
    form = PersonChangeForm
    add_form = PersonCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name', 'email', 'url', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    readonly_fields = ('date_created', 'date_modified', 'last_login', )
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'url', 'password', 'activation_key', )
        }),
        ('Dates', {
            'fields': ('date_created', 'date_activated', 'date_modified',
                                                                'last_login', )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                                               'groups', 'user_permissions')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'url', 'password1', 'password2')}
        ),
    )
    search_fields = ('name', 'email', 'url')
    ordering = ('name',)


admin.site.register(Person, PersonAdmin)
