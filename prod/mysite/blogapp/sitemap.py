from django.contrib.sitemaps import (
    Sitemap,
)

from .models import Article


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return (
            Article.objects.filter(pub_date__isnull=False)
            .defer("content")
            .order_by("-pub_date")
            .select_related("author", "category")
            .prefetch_related("tags")
            .all()[:5]
        )

    def lastmod(self, obj: Article):
        return obj.pub_date
