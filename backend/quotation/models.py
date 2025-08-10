from django.conf import settings
from django.db import models
from provider.models import Provider

class Quotation(models.Model):

    # Relación con el proveedor
    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name='quotations',
        verbose_name="proveedor"
    )

    date = models.DateTimeField(
        verbose_name="fecha de la cotización"
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        editable=False,
        verbose_name="código de cotización",
        help_text="Código único generado automáticamente para la cotización."
    )

    is_approved = models.BooleanField(
        default=None,
        verbose_name="aprobada",
        help_text="Marcar si la cotización ha sido aprobada."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"Cotización {self.code} - {self.provider.name}"

    def save(self, *args, **kwargs):

        if not self.pk:
            super().save(*args, **kwargs)
            # Genera el código usando la fecha y el ID. Ej: COT-20250809-00001
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"COT-{date_str}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'quotation'
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-date']