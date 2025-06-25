from django.db.models.base import Model
from django.utils.safestring import SafeText
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from blogapp.models import Article


class BlogIndexView(TemplateView):
    template_name = "blogapp/blog-index.html"


class ArticlesListView(ListView):
    queryset = (
        Article.objects.filter(pub_date__isnull=False)
        .defer("content")
        .order_by("-pub_date")
        .select_related("author", "category")
        .prefetch_related("tags")
        .all()
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles_list")

    def items(self):
        return (
            Article.objects.filter(pub_date__isnull=False)
            .defer("content")
            .order_by("-pub_date")
            .select_related("author", "category")
            .prefetch_related("tags")
            .all()[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
