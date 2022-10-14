import os
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


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
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
]


MIDDLEWARE = [
    # These modify the `Vary` header:
    # * SessionMiddleware (adds Cookie)
    # * GZipMiddleware (adds Accept-Encoding)
    # * LocaleMiddleware (adds Accept-Language)
    # Should go near top of the list:
    "django.middleware.security.SecurityMiddleware",
    # Above all other middleware apart from Django's SecurityMiddleware:
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

ROOT_URLCONF = "pepysdiary.common.urls"


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


CACHE_MIDDLEWARE_ALIAS = "default"
# Also see the CACHES setting in the server-specific settings files.
CACHE_MIDDLEWARE_SECONDS = 500
CACHE_MIDDLEWARE_KEY_PREFIX = "pepys"


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

SITE_ID = 1

AUTH_USER_MODEL = "membership.Person"

LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"
LOGOUT_URL = "logout"

COMMENTS_APP = "pepysdiary.annotations"

TEST_RUNNER = "pepysdiary.common.test_runner.PepysDiaryTestRunner"


TIME_ZONE = "UTC"

LANGUAGE_CODE = "en-gb"

USE_I18N = False

USE_L10N = True

USE_TZ = True


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
    DEFAULT_FILE_STORAGE = "pepysdiary.common.storage.MediaS3Boto3Storage"

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_QUERYSTRING_AUTH = False

    AWS_DEFAULT_ACL = "public-read"

    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com{MEDIA_URL}"


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
        "rich": {"datefmt": "[%X]"},
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "filters": ["require_debug_true"],
            "formatter": "rich",
            "level": "DEBUG",
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
        },
    },
    "loggers": {
        "django": {
            "handlers": [],
            "level": os.getenv("PEPYS_LOG_LEVEL", default="INFO"),
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("PEPYS_LOG_LEVEL", default="INFO"),
    },
}


PEPYS_CACHE = os.getenv("PEPYS_CACHE", default="memory")

if PEPYS_CACHE == "redis":
    # Use the TLS URL if set, otherwise, use the non-TLS one:
    REDIS_URL = os.getenv("REDIS_TLS_URL", default=os.getenv("REDIS_URL", default=""))
    if REDIS_URL != "":
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            }
        }
        if os.getenv("REDIS_TLS_URL", default=""):
            CACHES["default"]["OPTIONS"]["CONNECTION_POOL_KWARGS"] = {
                "ssl_cert_reqs": None
            }

elif PEPYS_CACHE == "dummy":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
# else use the default in-memory caching


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


####################################################################
# THIRD-PARTY APPS


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


HCAPTCHA_SITEKEY = os.getenv("HCAPTCHA_SITEKEY", default="")
HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", default="")

MAPBOX_MAP_ID = os.getenv("MAPBOX_MAP_ID", default="")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", default="")

PEPYS_GOOGLE_ANALYTICS_ID = os.getenv("PEPYS_GOOGLE_ANALYTICS_ID", default="")

# From http://akismet.com/
PEPYS_AKISMET_API_KEY = os.getenv("PEPYS_AKISMET_API_KEY", default="")


# Sentry
# https://devcenter.heroku.com/articles/sentry#integrating-with-python-or-django

SENTRY_DSN = os.getenv("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        release=os.getenv("HEROKU_SLUG_COMMIT", ""),
    )


####################################################################
# PEPYSDIARY SPECIFIC

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
YEARS_OFFSET = 353

# We have to do special things to some Encyclopedia Topics depending on
# whether they're in the 'People' category. So we need to store its ID:
PEOPLE_CATEGORY_ID = 2

# We have a Topic for Samuel Pepys, which occasionally needs special
# treatment, so we store its ID here:
PEPYS_TOPIC_ID = 29

PEPYS_MEMBERSHIP_BLACKLISTED_DOMAINS = [
    "bukhariansiddur.com",
    "spacehotline.com",
]
