from django.urls import path

from .views import (
    ArticlesListView,
    ArticleDetailView,
    BlogIndexView,
    LatestArticlesFeed,
)

app_name = "blogapp"


urlpatterns = [
    path("", BlogIndexView.as_view(), name="index"),
    path("articles/", ArticlesListView.as_view(), name="articles_list"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles-feed"),
]
