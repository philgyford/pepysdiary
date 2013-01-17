# coding: utf-8
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from pepysdiary.common.models import Config
from pepysdiary.membership import forms
from pepysdiary.membership.models import Person


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = forms.RegistrationForm

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
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


@csrf_protect
@never_cache
@sensitive_post_parameters('password')
def login(request, *args, **kwargs):
    """Wrapper for auth.login."""
    if request.user.is_authenticated():
        return redirect('home')
    else:
        kwargs['template_name'] = 'login.html'
        kwargs['authentication_form'] = forms.LoginForm
        auth_view_response = auth_views.login(request, *args, **kwargs)
        return auth_view_response


def logout(request, *args, **kwargs):
    """Wrapper for auth.logout."""
    if request.user.is_authenticated():
        kwargs['template_name'] = 'message.html'
        if 'extra_context' not in kwargs:
            kwargs['extra_context'] = {}
        kwargs['extra_context']['title'] = "You are now logged out"
        kwargs['extra_context']['message'] = "Thanks for coming."
        return auth_views.logout(request, *args, **kwargs)
    else:
        # Not logged in anyway!
        return redirect('home')


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

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(MessageView, self).dispatch(*args, **kwargs)

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
    title = "Thanks for registering."
    message = "An email has been sent to you containing a link. You'll need to click it to confirm your email address before you can log in."


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
    title = 'Thanks!'

    def get_message(self):
        return "Your email address is confirmed. You can now <a href=\"%s\">log in</a>." \
            % reverse('login')
