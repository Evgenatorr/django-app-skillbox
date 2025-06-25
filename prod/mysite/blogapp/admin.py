from django.contrib import admin

from .models import Article, Author, Tag, Category


class TagsInline(admin.StackedInline):
    model = Article.tags.through


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        TagsInline,
    ]
    list_display = (
        "pk",
        "title",
        "content",
        "pub_date",
        "author",
        "category",
        "tags_list",
    )
    list_display_links = "pk", "title"

    def get_queryset(self, request):
        return Article.objects.select_related("author", "category").prefetch_related(
            "tags"
        )

    def tags_list(self, obj: Article) -> str:
        return ", ".join([tag.name for tag in obj.tags.all()])


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = "name",  
    list_display_links = "name", 


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "name", 'bio', 
    list_display_links = "name", 


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "name", 
    list_display_links = "name", 
