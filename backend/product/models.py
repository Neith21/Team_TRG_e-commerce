import uuid
from django.conf import settings
from django.db import models
from category.models import Category
from subcategory.models import Subcategory
from unit_of_measure.models import UnitOfMeasure
from smart_selects.db_fields import ChainedForeignKey

class Product(models.Model):
    # --- Identificadores Únicos ---
    uuid = models.UUIDField(
        default=uuid.uuid4, # Genera un UUID v4 automáticamente
        editable=False,
        unique=True,
        verbose_name="UUID"
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        blank=True, # Permitimos que esté en blanco, ya que lo generaremos nosotros
        editable=False, # El usuario no debe poder editarlo
        verbose_name="código de producto",
        help_text="Código único generado automáticamente para el producto."
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="SKU (Stock Keeping Unit)",
        help_text="Código único de referencia para el inventario, usualmente del proveedor."
    )

    name = models.CharField(max_length=100, verbose_name="nombre del producto")
    size = models.CharField(max_length=100, verbose_name="talla o dimensión")
    description = models.TextField(null=True, blank=True, verbose_name="descripción")
    presentation = models.CharField(max_length=100, verbose_name="presentación")

    # --- Relaciones ---
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, # Evita borrar una categoría si tiene productos
        related_name='products',
        verbose_name="categoría"
    )
    subcategory = ChainedForeignKey(
        Subcategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        verbose_name="subcategoría",
        on_delete=models.PROTECT
    )
    purchase_unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="unidad de compra"
    )
    sale_unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="unidad de venta"
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # Generar el código solo al crear un nuevo producto
        if not self.pk:
            super().save(*args, **kwargs)
            # Ejemplo: CAT-SUBCAT-00001
            cat_prefix = self.category.name[:3].upper()
            subcat_prefix = self.subcategory.name[:3].upper()
            self.code = f"{cat_prefix}-{subcat_prefix}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'product'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']