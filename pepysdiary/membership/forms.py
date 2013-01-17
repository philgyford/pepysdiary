# coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from pepysdiary.common.models import Config
from pepysdiary.membership.models import Person
from pepysdiary.membership.utilities import validate_person_name
from pepysdiary.membership.widgets import Html5EmailInput


# Much of this based on django-registration.


attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    name = forms.CharField(max_length=50, validators=[validate_person_name],
                                        required=True, label=_("Your name"),
            help_text='Required. How people will know you. Can use spaces, eg "Samuel Pepys".')
    url = forms.URLField(label=_("URL"), max_length=255, required=False,
        help_text='Optional. eg, the address of your blog, Facebook page, Twitter page, etc.')
    email = forms.EmailField(required=True, label=_("Email address"),
                max_length=255, widget=Html5EmailInput(attrs=attrs_dict),
                help_text='Required. Will not be public.')
    password1 = forms.CharField(widget=forms.PasswordInput(
                                        attrs=attrs_dict, render_value=False),
                                        required=True, label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(
                                        attrs=attrs_dict, render_value=False),
                                    required=True, label=_("Repeat password"))

    def clean_name(self):
        """
        Validate that the name is alphanumeric and is not already
        in use.

        """
        existing = Person.objects.filter(
                                        name__iexact=self.cleaned_data['name'])
        if existing.exists():
            raise forms.ValidationError(_("That name has already been used."))
        else:
            return self.cleaned_data['name']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        config = Config.objects.get_site_config()
        if config is not None:
            if config.allow_registration == False:
                raise forms.ValidationError(
                    "Sorry, new registrations aren't allowed at the moment.")

        if 'password1' in self.cleaned_data and \
                                            'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != \
                                                self.cleaned_data['password2']:
                raise forms.ValidationError(_(
                                    "The two password fields didn't match."))
        return self.cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=Html5EmailInput(attrs=attrs_dict),
        max_length=255, label="Email address",
        error_messages={'invalid': u'Please enter a valid email address.'})
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict))

    def clean(self):
        config = Config.objects.get_site_config()
        if config is not None:
            if config.allow_login == False:
                raise forms.ValidationError(
                                    "Sorry, logging in is currently disabled.")
        return super(LoginForm, self).clean()

