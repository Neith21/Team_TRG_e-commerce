from django.conf import settings
from django.db import models
from buy_order.models import BuyOrder
from product.models import Product
from unit_of_measure.models import UnitOfMeasure

class BuyOrderDetail(models.Model):

    # --- Relaciones ---
    buy_order = models.ForeignKey(
        BuyOrder,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="orden de compra"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="producto"
    )
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        verbose_name="unidad de medida"
    )

    # --- Campos del Detalle ---
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="precio unitario"
    )
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="cantidad"
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"Detalle: {self.product.name} en Orden de Compra {self.buy_order.code}"

    class Meta:
        db_table = 'buy_order_detail'
        verbose_name = 'Detalle de Orden de Compra'
        verbose_name_plural = 'Detalles de Ordenes de Compra'
        ordering = ['buy_order', 'product__name']