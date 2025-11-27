import uuid
from django.conf import settings
from django.db import models
from branch.models import Branch
from product.models import Product
from inventory_movement_type.models import InventoryMovementType

class Inventory(models.Model):

    entry_number = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        verbose_name="número de entrada (UUID)"
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="sucursal")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="producto")
    batch = models.UUIDField(verbose_name="lote (batch)", editable=False)
    original_quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="cantidad original",
        help_text="La cantidad inicial con la que se creó este registro."
    )
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="cantidad actual",
        help_text="El saldo restante de este lote específico."
    )
    cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="costo unitario"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de ingreso")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última actualización")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        db_table = 'inventory'
        verbose_name = 'Inventario (Por Lote)'
        verbose_name_plural = 'Inventario (Por Lotes)'
        ordering = ['-created_at']
        unique_together = ('branch', 'product', 'batch')

    def __str__(self):
        return f"{self.product.name} - Lote: {str(self.batch)[:8]}... (Q: {self.quantity})"