from .base import *  # noqa: F401, F403
from .base import get_env_variable


CACHES = {
    "default": {
        # Use dummy cache (ie, no caching):
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = get_env_variable("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = get_env_variable("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_USE_SSL = True
