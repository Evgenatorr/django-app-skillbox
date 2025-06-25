from django.db import transaction
from django.core.management import BaseCommand

from blogapp.models import Article, Author, Category, Tag


class Command(BaseCommand):
    """
    Creates article
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create article")

        author, _ = Author.objects.get_or_create(name="Petya")
        category, _ = Category.objects.get_or_create(name="Asdf")
        tag, _ = Tag.objects.get_or_create(name="Zxc")
        article, _ = Article.objects.get_or_create(
            title="Dogs", content="About dogs", author=author, category=category
        )
        article.tags.add(tag)
        article.save()

        self.stdout.write(self.style.SUCCESS("Article created"))
