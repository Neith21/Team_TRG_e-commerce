from django.conf import settings
from django.db import models

class InventoryMovementType(models.Model):

    # --- Opciones de Flujo ---
    FLOW_CHOICES = (
        ('in', 'Entrada (+)'),
        ('out', 'Salida (-)'),
    )

    # --- Campos Principales ---
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre del movimiento",
        help_text="Ej: Ventas, Compras, Devolución, Avería."
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="código interno",
        help_text="Código único para referencia (Ej: TRAS-ENT, VENT, COMP)."
    )

    flow = models.CharField(
        max_length=10,
        choices=FLOW_CHOICES,
        verbose_name="flujo de inventario",
        help_text="Determina si este movimiento aumenta o disminuye el stock."
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="descripción",
        help_text="Descripción opcional del motivo del movimiento."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        sign = "+" if self.flow == 'in' else "-"
        return f"{self.name} ({sign})"

    class Meta:
        db_table = 'inventory_movement_type'
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimientos'
        ordering = ['name']