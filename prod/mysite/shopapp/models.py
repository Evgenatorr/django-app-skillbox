from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .validators import starting_with_letter


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk, filename=filename
    )


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk, filename=filename
    )


class Product(models.Model):
    """
    Модель Product представляет товар, который можно продавать в интернет-магазине.

    Заказы: :model:`shopapp.Order`
    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("product")
        verbose_name_plural = _("products")

    name = models.CharField(
        max_length=100, validators=[starting_with_letter], db_index=True
    )
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(99)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_directory_path,
        verbose_name=_("preview"),
    )

    # @property
    # def description_short(self):
    #     if len(self.description) < 50:
    #         return self.description
    #     return self.description[:48] + "..."

    def get_absolute_url(self):
        return reverse("shopapp:products_details", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        blank=True, upload_to=product_images_directory_path, verbose_name=_("image")
    )
    description = models.CharField(max_length=200, blank=True)


class Order(models.Model):
    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to="orders/receipts/")
