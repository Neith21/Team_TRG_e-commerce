from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class Client(models.Model):
    DEPARTMENT_CHOICES = (
        ('AH', 'Ahuachapán'),
        ('SA', 'Santa Ana'),
        ('SO', 'Sonsonate'),
        ('CH', 'Chalatenango'),
        ('LL', 'La Libertad'),
        ('SS', 'San Salvador'),
        ('CU', 'Cuscatlán'),
        ('LP', 'La Paz'),
        ('CA', 'Cabañas'),
        ('SV', 'San Vicente'),
        ('US', 'Usulután'),
        ('SM', 'San Miguel'),
        ('MO', 'Morazán'),
        ('LU', 'La Unión'),
    )
    dui_validator = RegexValidator(
        regex=r'^\d{8}-\d{1}$',
        message="El DUI debe tener el formato correcto: 00000000-0"
    )
    phone_validator = RegexValidator(
        regex=r'^\d{4}-\d{4}$',
        message="El teléfono debe tener el formato: 0000-0000"
    )
    first_name = models.CharField(max_length=100, verbose_name="nombres")
    last_name = models.CharField(max_length=100, verbose_name="apellidos")
    dui = models.CharField(
        max_length=10,
        unique=True, 
        verbose_name="DUI",
        validators=[dui_validator],
        help_text="Formato requerido: 00000000-0"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="email")
    phone = models.CharField(
        max_length=9,
        verbose_name="teléfono",
        validators=[phone_validator],
        help_text="Formato requerido: 0000-0000"
    )
    address = models.TextField(verbose_name="dirección completa")
    department = models.CharField(
        max_length=2, 
        choices=DEPARTMENT_CHOICES, 
        default='SS', 
        verbose_name="departamento"
    )
    municipality = models.CharField(max_length=100, verbose_name="municipio")
    is_tax_contributor = models.BooleanField(
        default=False, 
        verbose_name="es contribuyente (Crédito Fiscal)",
        help_text="Marcar si el cliente requiere Comprobante de Crédito Fiscal (CCF)."
    )
    nrc = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="NRC",
        help_text="Número de Registro de Contribuyente. Obligatorio si pide Crédito Fiscal."
    )
    business_line = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="giro",
        help_text="Actividad económica. Obligatorio si pide Crédito Fiscal."
    )

    # --- Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última actualización")

    class Meta:
        db_table = 'client'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.dui})"

    def clean(self):
        if self.is_tax_contributor:
            errors = {}
            if not self.nrc:
                errors['nrc'] = "El NRC es obligatorio para clientes de Crédito Fiscal."
            if not self.business_line:
                errors['business_line'] = "El Giro es obligatorio para clientes de Crédito Fiscal."
            
            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.upper()
        if self.last_name:
            self.last_name = self.last_name.upper()
        super().save(*args, **kwargs)