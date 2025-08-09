from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

class Provider(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="nombre del proveedor",
        help_text="Nombre completo o razón social del proveedor."
    )
    country = models.CharField(
        max_length=100,
        verbose_name="país",
        help_text="País de origen del proveedor."
    )
    address = models.TextField(
        verbose_name="dirección",
        help_text="Dirección física completa del proveedor."
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="teléfono",
        help_text="Número de teléfono de contacto.",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$', 
                message="El formato del teléfono no es válido. Ejemplo: +50377778888"
            )
        ]
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name="correo electrónico",
        help_text="Dirección de correo electrónico de contacto.",
        error_messages={
            'unique': "Ya existe un proveedor registrado con este correo electrónico."
        }
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
        db_table = 'provider'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']