from django.conf import settings
from django.db import models
from branch.models import Branch
from product.models import Product
from inventory_movement_type.models import InventoryMovementType
from inventory.models import Inventory

class Kardex(models.Model):
    # Registro origen (Compra ID, Venta ID, etc.)
    transaction_id = models.PositiveIntegerField(
        verbose_name="ID de registro (origen)",
        help_text="ID de la Compra, Venta o Traslado asociado."
    )
    document_number = models.CharField(
        max_length=100, 
        verbose_name="número de documento",
        help_text="Factura #123, Envío #456, etc."
    )
    movement_type = models.ForeignKey(InventoryMovementType, on_delete=models.PROTECT, verbose_name="tipo de movimiento")
    inventory_entry = models.ForeignKey(
        Inventory, 
        on_delete=models.PROTECT, 
        related_name='kardex_movements',
        verbose_name="número de entrada (origen)"
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="sucursal")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="producto")
    batch = models.UUIDField(verbose_name="lote (batch)")
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="cantidad movida",
        help_text="Positiva si entra, negativa si sale (visual)."
    )
    cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="costo unitario")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de ingreso")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última actualización")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        db_table = 'kardex'
        verbose_name = 'Kardex'
        verbose_name_plural = 'Kardex'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at.strftime('%d/%m/%Y')} - {self.movement_type.name} - {self.product.name}"