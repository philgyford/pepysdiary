from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views


app_name = "api"

router = DefaultRouter(trailing_slash=False)
router.register(r"categories", views.CategoryViewSet)
router.register(r"entries", views.EntryViewSet)
router.register(r"topics", views.TopicViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
