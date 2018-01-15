# coding: utf-8
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView

from pepysdiary.annotations.models import Annotation
from pepysdiary.common.models import Config
from pepysdiary.membership import forms
from pepysdiary.membership.models import Person


@method_decorator([csrf_protect, never_cache, sensitive_post_parameters('password1', 'password2')], name='dispatch')
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = forms.RegistrationForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return super(RegisterView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return reverse('register_complete')

    def form_valid(self, form):
        Person.objects.create_inactive_user(
            name=form.cleaned_data['name'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email'],
            url=form.cleaned_data['url'],
            site=get_current_site(self.request),
        )
        return super(RegisterView, self).form_valid(form)


class ProfileView(DetailView):
    """
    A general, public view of a user's details.
    PrivateProfileView inherits this for the logged-in user's private view.
    """
    model = Person
    queryset = Person.objects.filter(is_active=True)
    private_profile = False

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['private_profile'] = self.private_profile
        if self.object:
            comments_qs = Annotation.visible_objects.filter(user=self.object)
            context['comment_count'] = comments_qs.count()
            context['comment_list'] = comments_qs.order_by('-submit_date')[:10]
        return context

@method_decorator([never_cache], name='dispatch')
class PrivateProfileView(LoginRequiredMixin, ProfileView):
    """
    The logged-in user viewing themself.
    """
    private_profile = True

    def get_object(self, queryset=None):
        """
        Override so that we can get the logged-in user's Person object.
        """
        return self.request.user


@method_decorator([csrf_protect, never_cache], name='dispatch')
class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    A logged-in user editing their details.
    """
    model = Person
    form_class = forms.PersonEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('private_profile')


@method_decorator([csrf_protect, never_cache], name='dispatch')
@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class LoginView(auth_views.LoginView):
    authentication_form = forms.LoginForm
    template_name = 'login.html'


class LogoutView(auth_views.LogoutView):
    template_name = 'message.html'

    def get_context_data(self, **kwargs):
        context = super(LogoutView, self).get_context_data(**kwargs)
        context['title'] = 'You are now logged out'
        context['message'] = 'Thanks for coming.'
        return context


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'emails/password_reset.txt'
    form_class = forms.PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'password_reset.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'message.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetDoneView, self).get_context_data(**kwargs)
        context['title'] = 'Reset instructions sent'
        context['message'] = "We’ve sent instructions for resetting your password to the email address you submitted."
        return context


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = forms.SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'password_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'message.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetCompleteView, self).get_context_data(**kwargs)
        context['title'] = 'Password reset'
        context['message'] = "Your password has been changed. <a href=\"%s\">Now you can log in.</a>" % reverse('login')
        return context


@method_decorator(never_cache, name='dispatch')
class MessageView(TemplateView):
    """
    For displaying generic messages.
    You can probably pass 'title' and 'message' in from the URL conf, although
    I'm not keen on that, and subclassing this witl 'title' and 'message'
    attributes seems nicer.
    """
    template_name = 'message.html'
    title = 'Message'
    message = ''

    def get_title(self):
        if 'title' in self.kwargs:
            return self.kwargs['title']
        elif self.title:
            return self.title
        else:
            return ''

    def get_message(self):
        if 'message' in self.kwargs:
            return self.kwargs['message']
        elif self.message:
            return self.message
        else:
            return ''

    def get_context_data(self, **kwargs):
        context = super(MessageView, self).get_context_data(**kwargs)
        context['title'] = self.get_title()
        context['message'] = self.get_message()
        return context


class RegisterCompleteView(MessageView):
    """After the user has successfully filled in the Register form."""
    title = "Please check your email"
    message = "Nearly there… An email has been sent to you containing a link.<br><br>You'll need to click it to confirm your email address before you can log in."

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return super(RegisterCompleteView, self).get(
                                                    request, *args, **kwargs)


class ActivateView(MessageView):
    """
    By default we treat this as a failure, but redirect to the success view if
    it worked.
    """
    title = 'Oops'
    message = "Sorry, that doesn't look like a valid activation URL."

    def get(self, request, *args, **kwargs):
        # Check that registration is allowed, before we go any further:
        config = Config.objects.get_site_config()
        if config and config.allow_registration == False:
            self.message = "Sorry, registration isn't allowed at the moment. Please try again soon."
            return super(ActivateView, self).get(request, *args, **kwargs)
        else:
            # Registration allowed, so continue:
            person = Person.objects.activate_user(kwargs['activation_key'])
            if person:
                return redirect('activate_complete')
            else:
                return super(ActivateView, self).get(request, *args, **kwargs)


class ActivationCompleteView(MessageView):
    """After the user has successfully clicked the link in their Activation
    email.
    """
    title = 'Done!'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return super(ActivationCompleteView, self).get(
                                                    request, *args, **kwargs)

    def get_message(self):
        return "Your email address is confirmed and you are now registered.<br><br><a class=\"link-more\" href=\"%s\">You can now log in</a>" \
            % reverse('login')
