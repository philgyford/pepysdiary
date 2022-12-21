from django.urls import path

from pepysdiary.common.views import GoogleSearchView, HomeView, RecentView, SearchView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("google-search/", GoogleSearchView.as_view(), name="google-search"),
    path("search/", SearchView.as_view(), name="search"),
    path("recent/", RecentView.as_view(), name="recent"),
]
