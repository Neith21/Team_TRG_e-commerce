from django.conf import settings
from django.db import models
from provider.models import Provider
from quotation.models import Quotation

class BuyOrder(models.Model):

    # Relación con el proveedor
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name="proveedor"
    )

    # Relación con la cotización
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name="cotización"
    )

    date = models.DateField(
        verbose_name="fecha de la orden"
    )
    
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="código de orden",
        help_text="Código único para la orden de compra."
    )

    arrival_date = models.DateTimeField(
        verbose_name="fecha de llegada"
    )

    status = models.BooleanField(
        default=None,
        verbose_name="estatus",
        help_text="Marcar el estatus de la orden."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"Orden de Compra {self.code} - {self.provider.name}"

    def save(self, *args, **kwargs):

        if not self.pk:
            super().save(*args, **kwargs)
            # Genera el código usando la fecha y el ID. Ej: COT-20250809-00001
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"BUY-{date_str}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'buy_order'
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Ordenes de Compras'
        ordering = ['-date']