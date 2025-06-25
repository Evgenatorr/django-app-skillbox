"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from csv import DictWriter
from random import randrange
from timeit import default_timer

from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.syndication.views import Feed
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend

from .forms import CreateOrderForm, GroupForm, ProductForm
from .models import Product, Order, ProductImage

from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import ProductSerializer, OrderSerializer
from .utils import save_csv_products, save_csv_orders


logger = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        # DjangoFilterBackend,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]
    # filterset_fields = [
    #     'name',
    #     'description',
    #     'price',
    #     'discount',
    #     'archived',
    # ]
    ordering_fields = [
        "delivery_address",
        "user",
    ]

    @extend_schema(
        summary="Get one product by id",
        description="Retrieves product, return 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        },
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    @extend_schema(
        summary="Get a list of products",
        description="Get a list of products, returns a list of all products",
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({field: getattr(product, field) for field in fields})

        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            file=request.FILES["file"].file, encoding=request.encoding
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        # SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]

    # search_fields = [
    #     'name',
    #     'description',
    # ]
    filterset_fields = [
        "delivery_address",
        "user",
    ]
    ordering_fields = [
        "delivery_address",
        "user",
    ]

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "orders-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "delivery_address",
            "promocode",
            "user",
            "products",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for order in queryset:
            writer.writerow({field: getattr(order, field) for field in fields})

        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        orders = save_csv_orders(
            file=request.FILES["file"].file, encoding=request.encoding
        )
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class ShopIndexView(TemplateView):
    template_name = "shopapp/shop-index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = [
            ("Laptop", 1999),
            ("Desktop", 2999),
            ("Smartphone", 999),
        ]
        context["time_running"] = default_timer()
        context["products"] = products
        context["items"] = randrange(0, 10)
        logger.debug("Products for shop index %s", products)
        logger.info("Rendering shop index")
        return context


class GroupsListView(TemplateView):
    template_name = "shopapp/groups-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GroupForm()
        context["groups"] = Group.objects.prefetch_related("permissions").all()
        return context

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    context_object_name = "product"
    queryset = Product.objects.prefetch_related("images")


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class LatestProductsFeed(Feed):
    title = "Products"
    description = "Updates on product changes"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.prefetch_related("images")

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:50]


class OrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/order_list.html"
    
    def get_queryset(self):
        self.owner = User.objects.all()
        return self.owner
    

class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrderUpdateView(UpdateView):
    model = Order
    form_class = CreateOrderForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductCreateView(UserPassesTestMixin, CreateView):
    def test_func(self) -> bool | None:
        if self.request.user.is_superuser:
            return True
        return self.request.user.has_perm("shopapp.add_product")

    model = Product
    success_url = reverse_lazy("shopapp:products_list")
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(product=self.object, image=image)
        return response


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self) -> bool | None:
        if self.request.user.is_superuser:
            return True
        product = self.get_object()
        if (
            self.request.user.has_perm("shopapp.change_product")
            and product.created_by == self.request.user
        ):
            return True

    model = Product
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse("shopapp:products_details", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(product=self.object, image=image)
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    form_class = CreateOrderForm
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def test_func(self) -> bool | None:
        if self.request.user.is_staff:
            return True

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user_orders_list.html"

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs["user_id"])
        return Order.objects.filter(user=self.owner).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context


class UsersOrdersDataExportView(ListView):
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        owner_pk = kwargs.get("user_id")
        cache_key = str(owner_pk)
        serializer_data = cache.get(cache_key)
        if serializer_data is None:
            user = get_object_or_404(User, pk=owner_pk)
            orders_data = Order.objects.filter(user=user).select_related('user').order_by("pk")
            serializer_data = OrderSerializer(orders_data, many=True)
            cache.set(cache_key, serializer_data, 300)
        return JsonResponse({"orders": serializer_data.data})