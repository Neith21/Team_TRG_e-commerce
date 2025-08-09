from django.conf import settings
from django.db import models
from quotation.models import Quotation
from product.models import Product
from unit_of_measure.models import UnitOfMeasure

class QuotationDetail(models.Model):

    # --- Relaciones ---
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name="cotización"
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
    required_quantity = models.PositiveIntegerField(
        verbose_name="cantidad requerida"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="precio unitario"
    )
    approved_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="cantidad aprobada"
    )
    is_approved = models.BooleanField(
        default=None,
        verbose_name="aprobada",
        help_text="Marcar el item ha sido aprobado."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"Detalle: {self.product.name} en Cotización {self.quotation.code}"

    class Meta:
        db_table = 'quotation_detail'
        verbose_name = 'Detalle de Cotización'
        verbose_name_plural = 'Detalles de Cotizaciones'
        ordering = ['quotation', 'product__name']