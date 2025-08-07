from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre de la categoría",
        help_text="Nombre único para la categoría. Solo se permiten letras, números y espacios.",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚ]+$', # Solo letras, números y espacios
                message="El nombre solo puede contener letras, números y espacios."
            )
        ],
        error_messages={
            'unique': "Ya existe una categoría con este nombre.",
            'required': "El nombre de la categoría es obligatorio."
        }
    )
    description = models.TextField(
        null=True, # Permite que sea nulo en la BD
        blank=True, # Permite que esté vacío en formularios
        verbose_name="descripción",
        help_text="Descripción opcional de la categoría."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']