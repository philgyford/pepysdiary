This was v0.8 of django-registration.
https://bitbucket.org/ubernostrum/django-registration/downloads

I've made these changes:

1. Changed all imports of `User` to try and use `get_user_model()` instead. https://bitbucket.org/ubernostrum/django-registration/pull-request/30/django-15-compatibility-with-custom-user/diff

2. Changed URL confs from using `direct_to_template` to `TemplateView.as_view`. https://bitbucket.org/ubernostrum/django-registration/pull-request/27/use-templateview-instead-of/diff

