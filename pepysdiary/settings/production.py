import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401, F403
from .base import get_env_variable


DEBUG = False

ADMINS = [
    # ('Phil Gyford', 'phil@gyford.com'),
]

MANAGERS = ADMINS

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = get_env_variable("SENDGRID_USERNAME")
EMAIL_HOST_PASSWORD = get_env_variable("SENDGRID_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# If you *don't* want to prepend www to the URL, remove the setting from
# the environment entirely. Otherwise, set to 'True' (or anything tbh).
PREPEND_WWW = True


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": get_env_variable("REDIS_URL"),
        "KEY_PREFIX": "pepysdiary",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # If Redis is down, ignore exceptions:
            "IGNORE_EXCEPTIONS": True,
        },
    }
}


# Storing Media files on AWS.

DEFAULT_FILE_STORAGE = "pepysdiary.common.s3utils.MediaS3Boto3Storage"

AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME")

AWS_QUERYSTRING_AUTH = False

AWS_DEFAULT_ACL = "public-read"

S3_URL = "https://%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
# Store static and media files in separate directories:
MEDIA_URL = S3_URL + MEDIA_URL


# https
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django

SENTRY_DSN = os.environ.get("SENTRY_DSN")  # noqa: F405

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],  # noqa: F40
        integrations=[DjangoIntegration()],
        release=os.environ.get("HEROKU_SLUG_COMMIT", ""),  # noqa: F40
    )


#############################################################################
# PEPYSDIARY-SPECIFIC SETTINGS.

GOOGLE_ANALYTICS_ID = "UA-89135-2"

# From https://www.google.com/recaptcha/
RECAPTCHA_PUBLIC_KEY = get_env_variable("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = get_env_variable("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_USE_SSL = True

# Do we use Akismet/TypePad spam checking?
# True/False. If false, no posted comments are checked.
# If True, AKISMET_API_KEY must also be set.
USE_SPAM_CHECK = get_env_variable("USE_SPAM_CHECK")

# From http://akismet.com/
AKISMET_API_KEY = get_env_variable("AKISMET_API_KEY")
