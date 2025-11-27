from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import datetime

class Vehicle(models.Model):

    VEHICLE_TYPES = (
        ('motorcycle', 'Motocicleta'),
        ('sedan', 'Sedán / Pick-up'),
        ('panel', 'Panel de Carga'),
        ('light_truck', 'Camión Ligero (< 5 Ton)'),
        ('heavy_truck', 'Camión Pesado (> 5 Ton)'),
    )
    plate_validator = RegexValidator(
        regex=r'^[A-Z0-9-]{3,10}$',
        message="La placa debe contener solo letras mayúsculas, números y guiones (sin espacios). Ej: P-123-456, C123456"
    )
    brand = models.CharField(
        max_length=50, 
        verbose_name="marca",
        help_text="Ej: Toyota, Isuzu, Kia"
    )
    model = models.CharField(
        max_length=50, 
        verbose_name="modelo",
        help_text="Ej: Hilux, NPR, Forte"
    )
    year = models.PositiveIntegerField(
        verbose_name="año",
        validators=[
            MinValueValidator(1980), 
            MaxValueValidator(datetime.date.today().year + 1)
        ],
        help_text="Año de fabricación del vehículo."
    )
    plate = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[plate_validator],
        verbose_name="placa / matrícula",
        help_text="Número de placa único (se guardará en mayúsculas)."
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPES,
        default='sedan',
        verbose_name="tipo de vehículo"
    )
    max_capacity_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="capacidad máx. (Kg)",
        help_text="Peso máximo que soporta el vehículo."
    )
    driver_name = models.CharField(
        max_length=100, 
        verbose_name="nombre del conductor asignado",
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="observaciones",
        help_text="Detalles adicionales, estado mecánico, etc."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.plate} - {self.brand} {self.model}"

    def clean(self):
        current_year = datetime.date.today().year
        if self.year and self.year > current_year + 1:
            raise ValidationError({'year': 'El año del vehículo no puede ser mayor al año próximo.'})

    def save(self, *args, **kwargs):
        if self.plate:
            self.plate = self.plate.upper().strip()
        if self.brand:
            self.brand = self.brand.upper().strip()
        if self.model:
            self.model = self.model.upper().strip()
        if self.driver_name:
            self.driver_name = self.driver_name.title().strip()
            
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'vehicle'
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['plate']