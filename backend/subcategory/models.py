from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from category.models import Category

class Subcategory(models.Model):
    # Relación con la categoría padre
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE, # Si se borra la categoría, se borran sus subcategorías
        related_name='subcategories', # Para acceder desde una categoría: mi_categoria.subcategories.all()
        verbose_name="categoría padre"
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre de la subcategoría",
        help_text="Nombre único para la subcategoría.",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚ]+$',
                message="El nombre solo puede contener letras, números y espacios."
            )
        ],
        error_messages={
            'unique': "Ya existe una subcategoría con este nombre."
        }
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="descripción",
        help_text="Descripción opcional de la subcategoría."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        # Muestra el nombre de la subcategoría y su categoría padre para mayor claridad
        return f"{self.name} (Categoría: {self.category.name})"

    class Meta:
        db_table = 'subcategory'
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        ordering = ['category__name', 'name']