from .base import *
import dj_database_url


DEBUG = False

ADMINS = [
    # ('Phil Gyford', 'phil@gyford.com'),
]

MANAGERS = ADMINS

# Uses DATABASE_URL environment variable:
DATABASES = {'default': dj_database_url.config()}
DATABASES['default']['CONN_MAX_AGE'] = 500

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = get_env_variable('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = get_env_variable('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
PREPEND_WWW = True


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': get_env_variable('REDIS_URL'),
        'KEY_PREFIX': 'pepysdiary',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # If Redis is down, ignore exceptions:
            'IGNORE_EXCEPTIONS': True,
        },
    }
}


# https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# HSTS
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django
# via https://simonwillison.net/2017/Oct/17/free-continuous-deployment/# Step_4_Monitor_errors_with_Sentry_75

SENTRY_DSN = os.environ.get('SENTRY_DSN')

if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': os.environ.get('HEROKU_SLUG_COMMIT', ''),
    }

    # From https://docs.sentry.io/clients/python/integrations/django/
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR', # To capture more than ERROR, change to WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                # 'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }



#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_ANALYTICS_ID = 'UA-89135-2'

# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = get_env_variable('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = get_env_variable('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_USE_SSL = True

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = get_env_variable('USE_SPAM_CHECK')

# From http://akismet.com/
AKISMET_API_KEY = get_env_variable('AKISMET_API_KEY')
