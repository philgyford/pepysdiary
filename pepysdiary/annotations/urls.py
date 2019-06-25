from django.conf.urls import url

from .views import flag


urlpatterns = [
    # Our replacement for the default.
    url(r"^flag/(\d+)/$", flag, name="annotations-flag")
]
