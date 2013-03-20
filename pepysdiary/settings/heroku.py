from defaults import *
import os
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Phil Gyford', 'phil@gyford.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': dj_database_url.config(
                                    default=os.environ.get('DATABASE_URL'))}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

PREPEND_WWW = True

ALLOWED_HOSTS = ['.pepysdiary.com', 'pepysdiary.herokuapp.com', ]

os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')

CACHES = {
  'default': {
    'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
    'LOCATION': os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';'),
    'TIMEOUT': 500,
    'BINARY': True,
  }
}

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = os.environ.get('SECRET_KEY', '')

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

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# Store static and media files in separate directories:
STATIC_URL = S3_URL + STATIC_URL
MEDIA_URL = S3_URL + MEDIA_URL

# For django-compressor.
COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED')
COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = STATICFILES_STORAGE


#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')

# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_USE_SSL = True

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = os.environ.get('USE_SPAM_CHECK')

# From http://akismet.com/
AKISMET_API_KEY = os.environ.get('AKISMET_API_KEY')

# From http://cloudmade.com/
CLOUDMADE_API_KEY = os.environ.get('CLOUDMADE_API_KEY')
