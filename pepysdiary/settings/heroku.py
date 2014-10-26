from defaults import *
from os import environ
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Phil Gyford', 'phil@gyford.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': dj_database_url.config(
                                    default=environ.get('DATABASE_URL'))}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
PREPEND_WWW = environ.get('PREPEND_WWW', False)

ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', '*').split(',')

environ['MEMCACHE_SERVERS'] = environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
environ['MEMCACHE_USERNAME'] = environ.get('MEMCACHIER_USERNAME', '')
environ['MEMCACHE_PASSWORD'] = environ.get('MEMCACHIER_PASSWORD', '')

CACHES = {
  'default': {
    'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
    'LOCATION': environ.get('MEMCACHIER_SERVERS', '').replace(',', ';'),
    'TIMEOUT': 500,
    'BINARY': True,
  }
}

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = environ.get('SECRET_KEY', '')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


######################################################################
# S3 storage

DEFAULT_FILE_STORAGE = 'pepysdiary.common.s3utils.MediaS3BotoStorage'
STATICFILES_STORAGE = 'pepysdiary.common.s3utils.StaticS3BotoStorage'

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME')

S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# Store static and media files in separate directories:
STATIC_URL = S3_URL + STATIC_URL
MEDIA_URL = S3_URL + MEDIA_URL


#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_MAPS_API_KEY = environ.get('GOOGLE_MAPS_API_KEY')
GOOGLE_ANALYTICS_ID = environ.get('GOOGLE_ANALYTICS_ID')

# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_USE_SSL = True

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = environ.get('USE_SPAM_CHECK')

# From http://akismet.com/
AKISMET_API_KEY = environ.get('AKISMET_API_KEY')

# From http://mapbox.com/
MAPBOX_MAP_ID = environ.get('MAPBOX_MAP_ID')
MAPBOX_ACCESS_TOKEN = environ.get('MAPBOX_ACCESS_TOKEN')
