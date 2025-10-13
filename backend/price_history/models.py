from django.db import models
from product.models import Product
from django.conf import settings
from django.utils import timezone
from price_analysis_detail.models import PriceAnalysisDetail

class PriceHistory(models.Model):
    analysis_detail = models.ForeignKey(PriceAnalysisDetail, on_delete=models.PROTECT, related_name="price_entries", verbose_name="Detalle de Análisis de Origen")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="price_history", verbose_name="Producto")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    is_active = models.BooleanField(default=True, verbose_name="Precio Activo")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Activación")
    
    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            PriceHistory.objects.filter(product=self.product, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Activo" if self.is_active else "Inactivo"
        return f"Precio de {self.product.name}: ${self.sale_price} ({status})"

    class Meta:
        verbose_name = "Historial de Precio"
        verbose_name_plural = "Historiales de Precios"
        ordering = ['-start_date']

class ActivePrice(PriceHistory):
    class Meta:
        proxy = True
        verbose_name = "Precio Activo"
        verbose_name_plural = "Precios Activos"