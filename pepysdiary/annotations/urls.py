from django.urls import path

from .views import flag


urlpatterns = [
    # Our replacement for the default.
    path("flag/<int:comment_id>/", flag, name="annotations-flag")
]
