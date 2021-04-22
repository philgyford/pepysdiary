from .base import *  # noqa: F40
from .base import get_env_variable


DEBUG = True

ADMINS = [
    ("Phil Gyford", "phil@gyford.com"),
]

MANAGERS = ADMINS

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
# PREPEND_WWW = False

CACHES = {
    "default": {
        # In-memory caching:
        # 'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'TIMEOUT': 400, # seconds before expiring a cached item. None for never.
        # django-redis:
        # 'BACKEND': 'django_redis.cache.RedisCache',
        # 'LOCATION': get_env_variable('REDIS_URL'),
        # 'KEY_PREFIX': 'hines',
        # 'OPTIONS': {
        #     'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        # },
        # Use dummy cache (ie, no caching):
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE += [  # noqa: F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    INSTALLED_APPS += [  # noqa: F405
        "debug_toolbar",
        "django_extensions",
    ]

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }
    RESULTS_CACHE_SIZE = 100


#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_ANALYTICS_ID = "UA-89135-2"

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = True

# From http://akismet.com/
AKISMET_API_KEY = get_env_variable("AKISMET_API_KEY")
