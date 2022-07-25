from django.urls import include, path

# from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from . import views

app_name = "api"

router = DefaultRouter(trailing_slash=False)
router.register(r"categories", views.CategoryViewSet)
router.register(r"entries", views.EntryViewSet)
router.register(r"topics", views.TopicViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("docs/", include_docs_urls(title="The Diary of Samuel Pepys API")),
    path(
        "schema/",
        get_schema_view(
            title="The Diary of Samuel Pepys API",
            url="https://www.pepysdiary.com/",
            version="1.0.0",
        ),
        name="openapi-schema",
    ),
]
