# coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import ugettext_lazy as _

from captcha.fields import ReCaptchaField

from pepysdiary.common.models import Config
from pepysdiary.membership.models import Person
from pepysdiary.membership.utilities import validate_person_name


# Much of this based on django-registration.


attrs_dict = {'class': 'required form-control'}


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested name and email are not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    name = forms.CharField(
            widget=forms.TextInput(attrs=attrs_dict), max_length=50,
            validators=[validate_person_name], required=True,
            label=_("Your name"),
            help_text='How people will know you. Can use spaces, eg “Samuel Pepys”.')
    email = forms.EmailField(required=True, label=_("Email address"),
                max_length=254, widget=forms.EmailInput(attrs=attrs_dict),
                help_text='This will not be visible to others.')
    password1 = forms.CharField(widget=forms.PasswordInput(
                                        attrs=attrs_dict, render_value=False),
                                        required=True, label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(
                                        attrs=attrs_dict, render_value=False),
                                    required=True, label=_("Repeat password"))
    url = forms.URLField(
            widget=forms.URLInput(attrs=attrs_dict),
            label=_("Personal URL"), max_length=255, required=False,
            help_text='Optional. eg, the web address of your blog, Facebook page, Twitter page, etc.')

    honeypot = forms.CharField(required=False,
                            label=_('If you enter anything in this field '\
                                'your registration will be treated as spam'))

    def __init__(self, *args, **kwargs):
        """
        We might need to add captcha and question/answer anti-spam fields,
        depending on our site config.
        """
        super(RegistrationForm, self).__init__(*args, **kwargs)
        config = Config.objects.get_site_config()
        if config is not None:
            if config.use_registration_captcha == True:
                self.fields['captcha'] = ReCaptchaField(
                                    attrs={'theme': 'white', 'tabindex': 6, },
                                                    label=_("Anti-spam test"))
            if config.use_registration_question == True and \
                config.registration_question != '' and \
                config.registration_answer != '':
                self.fields['answer'] = forms.CharField(
                                    widget=forms.TextInput(attrs=attrs_dict),
                                    max_length=255, required=True,
                                    label=_(config.registration_question))

    def clean_name(self):
        """
        Validate that the name is alphanumeric and is not already in use.
        """
        existing = Person.objects.filter(
                                        name__iexact=self.cleaned_data['name'])
        if existing.exists():
            raise forms.ValidationError(_("That name has already been used."))
        else:
            return self.cleaned_data['name']

    def clean_email(self):
        """
        Validate that the email is not already in use.
        """
        existing = Person.objects.filter(
                                    email__iexact=self.cleaned_data['email'])
        if existing.exists():
            raise forms.ValidationError(
                                _("That email address has already been used."))
        else:
            return self.cleaned_data['email']

    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value

    def clean_answer(self):
        """
        Validate that the anti-spam question was answered successfully.
        """
        config = Config.objects.get_site_config()
        if config is not None:
            if self.cleaned_data['answer'].lower() == config.registration_answer.lower():
                return self.cleaned_data['answer']
            else:
                raise forms.ValidationError(_("Please try again."))

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
        widget=forms.EmailInput(attrs=attrs_dict),
        max_length=254, label="Email address",
        error_messages={'invalid': u'Please enter a valid email address.'})
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict))

    def clean(self):
        config = Config.objects.get_site_config()
        if config is not None:
            if config.allow_login == False:
                raise forms.ValidationError(
                                    "Sorry, logging in is currently disabled.")
        return super(LoginForm, self).clean()


class PersonEditForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('email', 'url', )

    def __init__(self, *args, **kwargs):
        super(PersonEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget=forms.TextInput(attrs=attrs_dict)
        self.fields['url'].widget=forms.TextInput(attrs=attrs_dict)

class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs=attrs_dict),
        max_length=254, label="Email address",
        error_messages={'invalid': u'Please enter a valid email address.'})


class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
                            label="New password",
                            widget=forms.PasswordInput(attrs=attrs_dict))
    new_password2 = forms.CharField(
                            label="Repeat password",
                            widget=forms.PasswordInput(attrs=attrs_dict))

