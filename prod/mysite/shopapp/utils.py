from io import TextIOWrapper
from csv import DictReader
from django.contrib.auth.models import User
from .models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(file, encoding=encoding)
    reader = DictReader(csv_file)
    user = User.objects.get(id=1)
    products = [Product(**row, created_by=user) for row in reader]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(file, encoding=encoding)
    reader = DictReader(csv_file)
    user = User.objects.get(id=1)
    orders = [Order(**row, user=user) for row in reader]
    Order.objects.bulk_create(orders)
    return orders
