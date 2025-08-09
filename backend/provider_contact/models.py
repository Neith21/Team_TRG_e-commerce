from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from provider.models import Provider

class ProviderContact(models.Model):

    # Relación con el proveedor
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name="proveedor"
    )
    
    first_name = models.CharField(
        max_length=100,
        verbose_name="nombre",
        help_text="Nombre de la persona de contacto."
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="apellido",
        help_text="Apellido de la persona de contacto."
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="teléfono",
        help_text="Número de teléfono del contacto.",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$', 
                message="El formato del teléfono no es válido. Ejemplo: +50377778888"
            )
        ]
    )
    email = models.EmailField(
        max_length=100,
        verbose_name="correo electrónico",
        help_text="Dirección de correo electrónico del contacto."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.provider.name})"

    class Meta:
        db_table = 'provider_contact'
        verbose_name = 'Contacto de Proveedor'
        verbose_name_plural = 'Contactos de Proveedores'
        ordering = ['provider__name', 'first_name']
