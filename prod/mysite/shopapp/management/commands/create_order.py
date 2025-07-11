from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="Test")
        products: Sequence[Product] = Product.objects.only("id").all()
        order, created = Order.objects.get_or_create(
            delivery_address="ul Pupkina, d 8",
            promocode="SALE1",
            user=user,
        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(f"Created order {order}")
