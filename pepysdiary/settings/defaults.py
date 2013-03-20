# Django settings for pepysdiary project.

# Should be extended by settings in, eg, production.py.
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static_collected/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'common', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    # Must be first:
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pepysdiary.common.middleware.VisitTimeMiddleware',
    # Must be last:
    'django.middleware.cache.FetchFromCacheMiddleware',
)

CACHE_MIDDLEWARE_ALIAS = 'default'
# Also see the CACHES setting in the server-specific settings files.
CACHE_MIDDLEWARE_SECONDS = 500
CACHE_MIDDLEWARE_KEY_PREFIX = 'pepys'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

ROOT_URLCONF = 'pepysdiary.common.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pepysdiary.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'treebeard/templates/',
    os.path.join(PROJECT_ROOT, 'templates', ),
    os.path.join(PROJECT_ROOT, 'templates', 'common', ),
    os.path.join(PROJECT_ROOT, 'templates', 'diary', ),
    os.path.join(PROJECT_ROOT, 'templates', 'encyclopedia', ),
    os.path.join(PROJECT_ROOT, 'templates', 'letters', ),
    os.path.join(PROJECT_ROOT, 'templates', 'news', ),
    os.path.join(PROJECT_ROOT, 'templates', 'membership', ),
)

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    # Needed for django-treebeard admin:
    'django.core.context_processors.request',
    'pepysdiary.common.context_processors.api_keys',
    'pepysdiary.common.context_processors.config',
    'pepysdiary.common.context_processors.date_formats',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.flatpages',
    'storages',
    'treebeard',
    'south',
    'gunicorn',
    'captcha',
    'compressor',
    'pepysdiary.common',
    'pepysdiary.diary',
    'pepysdiary.encyclopedia',
    'pepysdiary.letters',
    'pepysdiary.indepth',
    'pepysdiary.news',
    'pepysdiary.membership',
    'pepysdiary.events',
    'django.contrib.comments',
    'pepysdiary.annotations',
)

AUTH_USER_MODEL = 'membership.Person'

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

COMMENTS_APP = 'pepysdiary.annotations'

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

####################################################################
# THIRD-PARTY APPS

# django-compressor
COMPRESS_CSS_FILTERS = [
    # Creates absolute urls from relative ones.
    'compressor.filters.css_default.CssAbsoluteFilter',
    # CSS minimizer.
    'compressor.filters.cssmin.CSSMinFilter'
]

####################################################################
# PEPYSDIARY SPECIFIC

# For messages we send to users.
DEFAULT_FROM_EMAIL = 'do-not-reply@pepysdiary.com'
# For error messages.
SERVER_EMAIL = 'do-not-reply@pepysdiary.com'

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


# The IDs of the various Movable Type blogs that we do one-off imports of data
# from:
MT_DIARY_BLOG_ID = 3
MT_ENCYCLOPEDIA_BLOG_ID = 4
MT_IN_DEPTH_BLOG_ID = 19
MT_NEWS_BLOG_ID = 5
MT_STORY_SO_FAR_BLOG_ID = 6
MT_LETTERS_BLOG_ID = 38
