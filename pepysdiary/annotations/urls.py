from django.urls import re_path

from .views import flag


urlpatterns = [
    # Our replacement for the default.
    re_path(r"^flag/(\d+)/$", flag, name="annotations-flag")
]
