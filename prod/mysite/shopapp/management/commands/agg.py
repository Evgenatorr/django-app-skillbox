from django.core.management import BaseCommand
from django.db.models import Min, Max, Avg, Count, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo agg actions")

        # result = Product.objects.filter(name__contains='Smartphone').aggregate(
        #     max_price=Max('price'), min_price=Min('price'), avg_price=Avg('price'), count=Count('id')
        # )
        # print(result)
        orders = Order.objects.annotate(
            total=Sum("products__price"), products_count=Count("products")
        )

        for order in orders:
            print(
                f"Order #{order.id} "
                f"with {order.products_count} "
                f"Products worth {order.total}"
            )

        self.stdout.write(f"done")
