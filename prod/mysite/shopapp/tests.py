from string import ascii_letters
from random import choices
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.conf import settings
from shopapp.models import Product, Order


class ProductCreateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="SuperUser",
            email="qwerty@mail.ru",
            password="qwerty",
        )
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create_view(self):

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("shopapp:create_product"),
            {
                "name": self.product_name,
                "price": "109.99",
                "description": "This is a table",
                "discount": "10",
            },
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="NameTest", password="qwerty")
        cls.product_name = "".join(choices(ascii_letters, k=10))
        cls.product = Product.objects.create(name=cls.product_name, created_by=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:products_details", kwargs={"pk": self.product.pk}),
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:products_details", kwargs={"pk": self.product.pk}),
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "auth-group-fixture.json",
        "user-auth-group-fixture.json",
        "user-fixture.json",
        "products-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create_user(username="NameTest", password="qwerty")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "auth-group-fixture.json",
        "user-auth-group-fixture.json",
        "user-fixture.json",
        "products-fixture.json",
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(expected_data, products_data["products"])


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create_user(username="NameTest", password="qwerty")
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)
        cls.product_name = "".join(choices(ascii_letters, k=10))
        cls.product = Product.objects.create(name=cls.product_name, created_by=cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address="Pushkina",
            promocode="SALE",
            user=self.user,
        )
        self.order.products.add(self.product)

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk}),
        )
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        order = response.context["order"]
        self.assertEqual(order.pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "user-fixture.json",
        "products-fixture.json",
        "orders-fixture.json",
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create_user(username="TestUser", password="qwerty")
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(reverse("shopapp:orders-export"))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(expected_data, orders_data["orders"])
