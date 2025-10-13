from django.db import models
from django.utils import timezone
from proration.models import Proration
from django.conf import settings

class PriceAnalysis(models.Model):
    proration = models.OneToOneField(Proration, on_delete=models.PROTECT, verbose_name="Prorrateo de Origen")
    code = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Código de Análisis")
    invoice_number = models.CharField(max_length=100, editable=False, verbose_name="Factura de Compra")
    is_approved = models.BooleanField(default=False, verbose_name="Análisis Aprobado", help_text="Marcar para generar y activar los nuevos precios en el historial.")
    date = models.DateField(default=timezone.now, editable=False, verbose_name="Fecha de Análisis")
    
    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.invoice_number = self.proration.purchase.invoice_number
            super().save(*args, **kwargs)
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"ANL-{date_str}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Análisis de Precio"
        verbose_name_plural = "Análisis de Precios"
        ordering = ['-date']

