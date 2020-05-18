from functools import wraps

from django.shortcuts import redirect

from pepysdiary.common.models import Config


def allow(action):
    """
    A view decorator that lets us switch off certain views in the settings.
    Set an action to False in the site's Config object and add the decorator
    to a view to make it dependent on the setting. eg, if Config has an
    `allow_registration` attribute, then having:
        @allow('registration')
    on a view means the view can only be used if `allow_registration` is True.
    """

    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            config = Config.objects.get_site_config()
            # eg, 'allow_registration':
            attr = "allow_%s" % action
            if config and hasattr(config, attr) and getattr(config, attr) is True:
                return func(request, *args, **kwargs)
            else:
                return redirect("home")

        return wraps(func)(inner_decorator)

    return decorator
