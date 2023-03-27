import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView

from pepysdiary.annotations.models import Annotation
from pepysdiary.common.models import Config
from pepysdiary.common.views import PaginatedListView
from pepysdiary.membership import forms
from pepysdiary.membership.models import Person


@method_decorator(never_cache, name="dispatch")
class MessageView(TemplateView):
    """
    For displaying generic messages.
    You can probably pass 'title' and 'message' in from the URL conf, although
    I'm not keen on that, and subclassing this with 'title' and 'message'
    attributes seems nicer.
    """

    template_name = "membership/message.html"
    title = "Message"
    message = ""

    def get_title(self):
        return self.title

    def get_message(self):
        return self.message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["message"] = self.get_message()
        return context


class ActivateView(MessageView):
    """
    By default we treat this as a failure, but redirect to the success view if
    it worked.
    """

    title = "Oops"
    message = "Sorry, that doesn't look like a valid activation URL."

    def get(self, request, *args, **kwargs):
        # Check that registration is allowed, before we go any further:
        config = Config.objects.get_site_config()
        if config and config.allow_registration is False:
            self.message = (
                "Sorry, registration isn’t allowed at the moment. "
                "Please try again soon."
            )
            return super().get(request, *args, **kwargs)
        else:
            #  Registration allowed, so continue:
            person = Person.objects.activate_user(kwargs["activation_key"])
            if person:
                return redirect("activate_complete")
            else:
                return super().get(request, *args, **kwargs)


class ActivateCompleteView(MessageView):
    """After the user has successfully clicked the link in their Activation
    email.
    """

    title = "Done!"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return super().get(request, *args, **kwargs)

    def get_message(self):
        return (
            "Your email address is confirmed and you are now registered."
            '<br><br><a class="link-more" href="%s">You can now log in</a>'
            % reverse("login")
        )


@method_decorator([csrf_protect, never_cache], name="dispatch")
class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    A logged-in user editing their details.
    """

    model = Person
    form_class = forms.PersonEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("private_profile")


@method_decorator([csrf_protect, never_cache], name="dispatch")
@method_decorator(sensitive_post_parameters("password"), name="dispatch")
class LoginView(auth_views.LoginView):
    authentication_form = forms.LoginForm
    template_name = "membership/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        "Override so we can add a message for the user."
        user = form.get_user()
        messages.success(self.request, "You’re now logged in as %s." % user.name)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    template_name = "membership/message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "You are now logged out"
        context["message"] = "Thanks for coming."
        return context


class PasswordResetView(auth_views.PasswordResetView):
    """The form where the user enters their address to receive a reset link

    Note: If they enter an email address that doesn't exist in the database this
    will still look like they've been sent an email - we don't show an error message -
    but no email is sent.
    """

    email_template_name = "membership/emails/password_reset_email.txt"
    form_class = forms.PasswordResetForm
    success_url = reverse_lazy("password_reset_done")
    template_name = "membership/password_reset.html"


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    "The page after submitting their email address to receive a reminder."

    template_name = "membership/message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Reset instructions sent"
        context["message"] = (
            "We’ve sent instructions for resetting your password to the "
            "email address you submitted."
        )
        return context


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    "The page the user gets to after clicking the link in a password reset email."

    form_class = forms.SetPasswordForm
    success_url = reverse_lazy("password_reset_complete")
    template_name = "membership/password_confirm.html"


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    "The page the user is redirected to after successfully changing their email address"

    template_name = "membership/message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Password reset"
        context["message"] = (
            'Your password has been changed. <a href="%s">Now you can log in.</a>'
            % reverse("login")
        )
        return context


class ProfileView(SingleObjectMixin, PaginatedListView):
    """
    A general, public view of a user's details.
    PrivateProfileView inherits this for the logged-in user's private view.

    SingleObjectMixin handles the Person object.
    PaginatedListView handles the Annotations (comment_list).
    """

    is_private_profile = False
    template_name = "membership/person_detail.html"
    paginate_by = 20
    allow_empty = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=Person.objects.filter(is_active=True).all()
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_private_profile"] = self.is_private_profile
        context["comment_list"] = context["object_list"]
        return context

    def get_queryset(self):
        return Annotation.visible_objects.filter(user=self.object).order_by(
            "-submit_date"
        )


@method_decorator([never_cache], name="dispatch")
class PrivateProfileView(LoginRequiredMixin, ProfileView):
    """
    The logged-in user viewing themself.
    """

    is_private_profile = True

    def get_object(self, queryset=None):
        """
        Override so that we can get the logged-in user's Person object.
        """
        return self.request.user


@method_decorator(
    [csrf_protect, never_cache, sensitive_post_parameters("password1", "password2")],
    name="dispatch",
)
class RegisterView(FormView):
    template_name = "membership/register.html"
    form_class = forms.RegistrationForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("register_complete")

    def form_valid(self, form):
        """
        Create the user unless their email or url look dodgy.
        In that case we do everything as usual except create the user.
        No error message or anything.
        """
        email = form.cleaned_data["email"]
        url = form.cleaned_data["url"]

        if self._form_data_is_good(email, url):
            Person.objects.create_inactive_user(
                name=form.cleaned_data["name"],
                password=form.cleaned_data["password1"],
                email=email,
                url=form.cleaned_data["url"],
                site=get_current_site(self.request),
            )

        return super().form_valid(form)

    def _form_data_is_good(self, email, url):
        """
        Is the data from the form maybe legitimate?

        * Rejects any emails witha  domain in blacklisted domains
        * Rejects any urls that are just IP addresses

        Returns boolean
        """
        bad_domains = settings.PEPYS_MEMBERSHIP_BLACKLISTED_DOMAINS
        if email.split("@")[1] in bad_domains:
            return False
        elif re.match(r"https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url):
            # It'll match technically invalid IP addresses but that's fine.
            return False
        else:
            print("C")
            return True


class RegisterCompleteView(MessageView):
    """After the user has successfully filled in the Register form."""

    title = "Please check your email"
    message = "Nearly there… An email has been sent to you containing a link"
    "<br><br>You'll need to click it to confirm your email address "
    "before you can log in."

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return super().get(request, *args, **kwargs)
