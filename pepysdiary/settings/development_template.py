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
        # Use dummy cache (ie, no caching):
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',

        # Or use local memcached:
        # 'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        # 'LOCATION': '127.0.0.1:11211',
    }
}

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = ''

# Debug Toolbar settings.
if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    INSTALLED_APPS += ('debug_toolbar', )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
    INTERNAL_IPS = ('127.0.0.1', )

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Needs to be your IP address, or 127.0.0.1, if DEBUG==True.
ALLOWED_HOSTS = ['127.0.0.1', ]

# Settings used only when importing the legacy data from the Movable Type
# MySQL database using management commands.
MT_MYSQL_DB_NAME = ''
MT_MYSQL_DB_USER = ''
MT_MYSQL_DB_PASSWORD = ''
MT_MYSQL_DB_HOST = ''


######################################################################
# Uncomment these to use S3 for storage:

# DEFAULT_FILE_STORAGE = 'pepysdiary.common.s3utils.MediaS3BotoStorage'
# STATICFILES_STORAGE = 'pepysdiary.common.s3utils.StaticS3BotoStorage'

# AWS_ACCESS_KEY_ID = ''
# AWS_SECRET_ACCESS_KEY = ''
# AWS_STORAGE_BUCKET_NAME = ''

# S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# # Store static and media files in separate directories:
# STATIC_URL = S3_URL + STATIC_URL
# MEDIA_URL = S3_URL + MEDIA_URL

# # For django-compressor.
# # You could just uncomment COMPRESS_ENABLED to have it compress files locally.
# COMPRESS_ENABLED = True
# COMPRESS_URL = STATIC_URL
# COMPRESS_STORAGE = STATICFILES_STORAGE
# COMPRESS_OFFLINE = True


#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_MAPS_API_KEY = ''
GOOGLE_ANALYTICS_ID = ''

# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_USE_SSL = True

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = True

# From http://akismet.com/
AKISMET_API_KEY = ''

# From http://cloudmade.com/
CLOUDMADE_API_KEY = ''
