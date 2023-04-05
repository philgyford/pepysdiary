import os
from datetime import datetime, timezone
from pathlib import Path

import dj_database_url
import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Loads env variables from .env:
load_dotenv()


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DEBUG", default="False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")


ADMINS = [("Phil Gyford", "phil@gyford.com")]

MANAGERS = ADMINS

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.sitemaps",
    "django.contrib.flatpages",
    # For fulltext searching on annotations:
    # 'django.contrib.postgres',
    "treebeard",
    "gunicorn",
    "hcaptcha",
    "rest_framework",
    "pepysdiary.common",
    "pepysdiary.api",
    "pepysdiary.diary",
    "pepysdiary.encyclopedia",
    "pepysdiary.letters",
    "pepysdiary.indepth",
    "pepysdiary.news",
    "pepysdiary.membership",
    "pepysdiary.events",
    "django_comments",
    "pepysdiary.annotations",
    "pepysdiary.up",
]


MIDDLEWARE = [
    # These modify the `Vary` header:
    # * SessionMiddleware (adds Cookie)
    # * GZipMiddleware (adds Accept-Encoding)
    # * LocaleMiddleware (adds Accept-Language)
    # Should go near top of the list:
    "django.middleware.security.SecurityMiddleware",
    # Must be before those that modify the `Vary` header:
    "django.middleware.cache.UpdateCacheMiddleware",
    # Before any middleware that may change or use the response body:
    "django.middleware.gzip.GZipMiddleware",
    # After GZipMiddleware and close to top:
    "django.middleware.common.CommonMiddleware",
    # After UpdateCacheMiddleware:
    "django.contrib.sessions.middleware.SessionMiddleware",
    # After SessionMiddleware:
    "django.middleware.csrf.CsrfViewMiddleware",
    # After SessionMiddleware:
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # After SessionMiddleware:
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "pepysdiary.common.middleware.VisitTimeMiddleware",
    # Must be before those that modify the `Vary` header:
    "django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "pepysdiary.config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["pepysdiary/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "pepysdiary.common.context_processors.api_keys",
                "pepysdiary.common.context_processors.config",
                "pepysdiary.common.context_processors.date_formats",
                "pepysdiary.common.context_processors.url_name",
            ]
        },
    }
]

WSGI_APPLICATION = "pepysdiary.config.wsgi.application"


DATABASES = {"default": dj_database_url.config(conn_max_age=500)}
DATABASES["default"]["OPTIONS"] = {"server_side_binding": True}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"
LOGOUT_URL = "logout"

COMMENTS_APP = "pepysdiary.annotations"

TEST_RUNNER = "pepysdiary.common.test_runner.PepysDiaryTestRunner"


TIME_ZONE = "UTC"

LANGUAGE_CODE = "en-gb"

USE_I18N = False

USE_TZ = True


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_ROOT = BASE_DIR / "pepysdiary" / "static_collected"

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "pepysdiary" / "common" / "static"]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]


MEDIA_ROOT = BASE_DIR / "pepysdiary" / "media"

MEDIA_URL = "/media/"


if os.getenv("PEPYS_USE_AWS_FOR_MEDIA", default="False") == "True":
    # Storing Media files on AWS.
    STORAGES["default"]["BACKEND"] = "pepysdiary.common.storage.MediaS3Boto3Storage"

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_QUERYSTRING_AUTH = False

    AWS_DEFAULT_ACL = "public-read"

    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com{MEDIA_URL}"


SITE_ID = 1

AUTH_USER_MODEL = "membership.Person"

# Monday:
FIRST_DAY_OF_WEEK = 1

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


PEPYS_USE_HTTPS = os.getenv("PEPYS_USE_HTTPS", default="False") == "True"

if PEPYS_USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Some tips: https://www.reddit.com/r/django/comments/x2h6cq/whats_your_logging_setup/
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "superverbose": {
            "format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(process)d %(thread)d %(message)s"  # noqa: E501
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            # "filters": ["require_debug_true"],
            "formatter": "verbose",
        },
    },
    "loggers": {
        "commands": {
            # For management commands and tasks where we specify the "commands" logger
            "handlers": ["console"],
            "propagate": True,
            "level": os.getenv("PEPYS_LOG_LEVEL", default="INFO"),
        },
        "django": {
            "handlers": ["console"],
            "level": os.getenv("PEPYS_LOG_LEVEL", default="INFO"),
        },
    },
    # "root": {"handlers": ["console"], "level": "INFO"},
}


PEPYS_CACHE_TYPE = os.getenv("PEPYS_CACHE_TYPE", default="dummy")
REDIS_URL = os.getenv("REDIS_URL", "")

if PEPYS_CACHE_TYPE == "memory":
    # Use in-memory caching
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "PEPYS",
        }
    }

elif PEPYS_CACHE_TYPE == "redis" and REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }

else:
    # Use dummy cache (ie, no caching)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

# Seconds before expiring a cached item. None for never expiring.
CACHES["default"]["TIMEOUT"] = 300


if os.getenv("SENDGRID_USERNAME", default=""):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_HOST_USER = os.getenv("SENDGRID_USERNAME")
    EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_PASSWORD")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True


if DEBUG:
    # Changes for local development

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


########################################################################################
# THIRD-PARTY APP SETTINGS


# django-rest-framework ################################################

REST_FRAMEWORK = {
    "ALLOWED_VERSIONS": ["v1"],
    # e.g. for latitude/longitude:
    "COERCE_DECIMAL_TO_STRING": False,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
    "DEFAULT_PAGINATION_CLASS": "pepysdiary.api.pagination.CustomPagination",
    "DEFAULT_RENDERER_CLASSES": (
        "pepysdiary.api.renderers.PrettyJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "60/minute", "user": "60/minute"},
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v1",
    "EXCEPTION_HANDLER": "pepysdiary.api.views.custom_exception_handler",
    "PAGE_SIZE": 50,
    "URL_FORMAT_OVERRIDE": None,
}

# hcaptcha #############################################################

HCAPTCHA_SITEKEY = os.getenv("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", default="")


# sentry-sdk ###########################################################
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django

SENTRY_DSN = os.getenv("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.01,
    )

# END THIRD-PARTY APP SETTINGS
########################################################################################

########################################################################################
# PEPYSDIARY SPECIFIC SETTINGS

PEPYS_CLOUDFLARE_ANALYTICS_TOKEN = os.getenv(
    "PEPYS_CLOUDFLARE_ANALYTICS_TOKEN", default=""
)

# From http://akismet.com/
PEPYS_AKISMET_API_KEY = os.getenv("PEPYS_AKISMET_API_KEY", default="")

MAPBOX_MAP_ID = os.getenv("MAPBOX_MAP_ID", default="")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", default="")

# For messages we send to users.
DEFAULT_FROM_EMAIL = "do-not-reply@pepysdiary.com"

# For error messages.
SERVER_EMAIL = "do-not-reply@pepysdiary.com"

# Where emails about flagged comments should be sent to.
COMMENT_FLAG_EMAIL = "phil@gyford.com"

# How many days do we give people to activate their account after registering?
# If we run the cleanupactivation command, it will delete any dormant
# activations older than this:
ACCOUNT_ACTIVATION_DAYS = 7

# How many years ahead of the diary entries are we?
YEARS_OFFSET = 363

# We have to do special things to some Encyclopedia Topics depending on
# whether they're in the 'People' category. So we need to store its ID:
PEOPLE_CATEGORY_ID = 2

# We have a Topic for Samuel Pepys, which occasionally needs special
# treatment, so we store its ID here:
PEPYS_TOPIC_ID = 29

# When did each 'reading' of the diary begin?
# Used to mark which annotations belong to which reading.
PEPYS_READING_DATETIMES = [
    datetime(2002, 12, 26, 0, 0, 0, tzinfo=timezone.utc),
    datetime(2013, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
]

PEPYS_MEMBERSHIP_BLACKLISTED_DOMAINS = [
    "bukhariansiddur.com",
    "ctopicsbh.com",
    "densebpoqq.com",
    "hbviralbv.com",
    "karenkey.com",
    "lanceuq.com",
    "leaderssk.com",
    "nightorb.com",
    "passedil.com",
    "rapidlyws.com",
    "spacehotline.com",
    "triots.com",
    "ustudentli.com",
    "vsmethodu.com",
    "vtqreplaced.com",
]

# END PEPYSDIARY SPECIFIC SETTINGS
########################################################################################
