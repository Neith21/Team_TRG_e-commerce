from django.conf import settings
from django.db import models
from buy_order.models import BuyOrder
from provider.models import Provider
import uuid

class Purchase(models.Model):
    # --- Relación Clave ---
    buy_order = models.ForeignKey(
        BuyOrder,
        on_delete=models.PROTECT,
        related_name='purchase',
        verbose_name="orden de compra",
        unique=True,
        help_text="Orden de compra a partir de la cual se genera esta compra."
    )

    # --- Campos de la Compra ---
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="número de factura",
        help_text="Número de factura o comprobante de crédito fiscal."
    )
    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="proveedor",
        editable=False
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        editable=False,
        verbose_name="código de compra",
        help_text="Código único generado automáticamente para la compra."
    )
    batch = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="lote (batch)",
        help_text="Código de lote único generado automáticamente."
    )
    date = models.DateField(
        verbose_name="fecha de compra"
    )
    is_approved = models.BooleanField(
    default=False,
    verbose_name="aprobada",
    help_text="Marcar si la compra ha sido aprobada."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"Compra {self.invoice_number} (Orden: {self.buy_order.code})"

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            # Genera el código usando la fecha y el ID. Ej: PUR-20251011-00001
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"PUR-{date_str}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'purchase'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-date']