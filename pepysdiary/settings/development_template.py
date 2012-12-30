from defaults import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    INSTALLED_APPS += ('debug_toolbar', )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
    INTERNAL_IPS = ('127.0.0.1', )

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

GOOGLE_MAPS_API_KEY = ''
GOOGLE_ANALYTICS_ID = ''


# Settings used only when importing the legacy data from the Movable Type
# MySQL database using management commands.
MT_MYSQL_DB_NAME = ''
MT_MYSQL_DB_USER = ''
MT_MYSQL_DB_PASSWORD = ''
MT_MYSQL_DB_HOST = ''
