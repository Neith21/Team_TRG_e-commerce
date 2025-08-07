from django.conf import settings
from django.db import models

class UnitOfMeasure(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="nombre de la unidad"
    )
    type = models.CharField(
        max_length=100,
        verbose_name="tipo de unidad",
        help_text="Campo de texto libre para el tipo de unidad (ej. 'Peso', 'Volumen')."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        db_table = 'unit'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        # La combinación de 'nombre' y 'tipo' debe ser única.
        unique_together = [['name', 'type']]
        ordering = ['name', 'type']