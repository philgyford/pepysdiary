from defaults import *
from os import environ

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = [
    ('Phil Gyford', 'phil@gyford.com'),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ.get('DB_NAME'),
        'USER': environ.get('DB_USERNAME'),
        'PASSWORD': environ.get('DB_PASSWORD'),
        'HOST': environ.get('DB_HOST'),
        'PORT': '',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
PREPEND_WWW = True

ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', '*').split(',')

CACHES = {
    'default': {
        # Use dummy cache (ie, no caching):
        #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',

        # Or use local memcached:
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 500, # millisecond
    }
}

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = environ.get('SECRET_KEY', '')

# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    INSTALLED_APPS += ['debug_toolbar', ]
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        # Force the toolbar to show as INTERNAL_IPS wasn't working with Vagrant.
        'SHOW_TOOLBAR_CALLBACK': "%s.true" % __name__
    }
    INTERNAL_IPS = ['127.0.0.1', '192.168.33.1', '0.0.0.0']

    def true(request):
        return True


#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_ANALYTICS_ID = 'UA-89135-2'

# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_USE_SSL = True

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = True

# From http://akismet.com/
AKISMET_API_KEY = environ.get('AKISMET_API_KEY')

# From http://mapbox.com/
MAPBOX_MAP_ID = 'philgyford.hnhb28lo'
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoicGhpbGd5Zm9yZCIsImEiOiJUUGpZME9zIn0.O3bxMZ-0-Fq-e0HwR6-xcA';
