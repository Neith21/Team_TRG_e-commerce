from django.conf import settings
from django.db import models
from purchase.models import Purchase
from product.models import Product
from unit_of_measure.models import UnitOfMeasure

class PurchaseDetail(models.Model):
    # --- Relaciones ---
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="compra"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="producto")
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, verbose_name="unidad de medida")

    # --- Campos del Detalle ---
    quantity = models.PositiveIntegerField(verbose_name="cantidad")
    verified_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="cantidad verificada",
        help_text="Cantidad real contada físicamente en bodega."
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="precio unitario")
    is_received = models.BooleanField(
        default=False,
        verbose_name="recibido",
        help_text="Marcar si este ítem específico ha sido recibido."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"Detalle de {self.product.name} en Compra {self.purchase.invoice_number}"

    class Meta:
        db_table = 'purchase_detail'
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compras'
        ordering = ['purchase', 'product__name']