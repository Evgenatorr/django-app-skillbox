from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")

        user = User.objects.get(pk=1)

        # result = Product.objects.filter(name__contains='Smartphone').update(discount=10)

        products_info = [
            ("Smartphone 1", 129),
            ("Smartphone 2", 149),
            ("Smartphone 3", 169),
        ]

        products = [
            Product(name=name, price=price, created_by=user)
            for name, price in products_info
        ]

        result = Product.objects.bulk_create(products)
        for obj in result:
            print(obj)

        self.stdout.write(f"done")
