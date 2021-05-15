from .base import *  # noqa: F401, F403


CACHES = {
    "default": {
        # Use dummy cache (ie, no caching):
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Don't use S3 for tests
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "..", "tests", "_media")
MEDIA_URL = "/media/"
