from django.conf import settings
from django.db import models

class Branch(models.Model):

    BRANCH_TYPES = (
        ('storage', 'Bodega'),
        ('branch', 'Sucursal'),
    )

    DEPARTMENTS_SV = (
        ('AH', 'Ahuachapán'),
        ('CB', 'Cabañas'),
        ('CH', 'Chalatenango'),
        ('CU', 'Cuscatlán'),
        ('LL', 'La Libertad'),
        ('LP', 'La Paz'),
        ('LU', 'La Unión'),
        ('MO', 'Morazán'),
        ('SM', 'San Miguel'),
        ('SS', 'San Salvador'),
        ('SV', 'San Vicente'),
        ('SA', 'Santa Ana'),
        ('SO', 'Sonsonate'),
        ('US', 'Usulután'),
    )

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="nombre de sucursal"
    )

    branch_type = models.CharField(
        max_length=20,
        choices=BRANCH_TYPES,
        default='branch',
        verbose_name="tipo"
    )

    address = models.TextField(
        verbose_name="dirección completa",
        help_text="Dirección física detallada."
    )

    department = models.CharField(
        max_length=2,
        choices=DEPARTMENTS_SV,
        default='SS',
        verbose_name="departamento"
    )

    municipality = models.CharField(
        max_length=100,
        verbose_name="municipio",
        help_text="Ej: Santa Tecla, Antiguo Cuscatlán, etc."
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="teléfono",
        help_text="Teléfono de contacto de la sucursal."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.name} ({self.get_branch_type_display()})"

    class Meta:
        db_table = 'branch'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ['name']