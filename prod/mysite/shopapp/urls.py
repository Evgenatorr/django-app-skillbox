from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import (
    ProductDetailsView,
    ShopIndexView,
    GroupsListView,
    ProductsListView,
    OrdersListView,
    ProductCreateView,
    OrderCreateView,
    OrderDetailView,
    ProductUpdateView,
    ProductDeleteView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsDataExportView,
    OrdersDataExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed,
    UserOrdersListView,
    UsersOrdersDataExportView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    # path("", cache_page(60 * 2)(ShopIndexView.as_view()), name="index"),
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create/", ProductCreateView.as_view(), name="create_product"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="products_details"),
    path(
        "products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"
    ),
    path(
        "products/<int:pk>/confirm-delete/",
        ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path("products/latest/feed/", LatestProductsFeed(), name="products-feed"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/create/", OrderCreateView.as_view(), name="create_order"),
    path("orders/export/", OrdersDataExportView.as_view(), name="orders-export"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path(
        "orders/<int:pk>/confirm-delete/",
        OrderDeleteView.as_view(),
        name="order_delete",
    ),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders_list_view"),
    path("users/<int:user_id>/orders/export/", UsersOrdersDataExportView.as_view(), name="user-orders-export"),
]
