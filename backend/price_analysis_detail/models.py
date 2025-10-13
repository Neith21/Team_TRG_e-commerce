from django.db import models
from product.models import Product
from django.conf import settings
from price_analysis.models import PriceAnalysis

class PriceAnalysisDetail(models.Model):
    analysis = models.ForeignKey(PriceAnalysis, on_delete=models.CASCADE, related_name="details")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Producto")
    quantity = models.PositiveIntegerField(editable=False, verbose_name="Cantidad")
    invoice_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False, verbose_name="Costo Factura (FOB)")
    final_prorated_cost = models.DecimalField(max_digits=12, decimal_places=4, editable=False, verbose_name="Costo Final Prorrateado")
    utility = models.DecimalField(max_digits=5, decimal_places=2, default=0.20, verbose_name="Utilidad (%)", help_text="Utilidad deseada en formato decimal. Ej: 0.25 para 25%.")
    
    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def sale_price(self):
        if self.utility >= 1:
            return self.final_prorated_cost
        return self.final_prorated_cost / (1 - self.utility)

    def __str__(self):
        return f"Detalle de {self.product.name} para {self.analysis.code}"
    
    class Meta:
        verbose_name = "Detalle de Análisis de Precio"
        verbose_name_plural = "Detalles de Análisis de Precios"
        unique_together = ('analysis', 'product')