from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from client.models import Client
from branch.models import Branch
from product.models import Product

class Sale(models.Model):
    SALE_TYPE_CHOICES = (
        ('FCF', 'Factura Consumidor Final'),
        ('CCF', 'Comprobante de Crédito Fiscal'),
    )
    STATUS_CHOICES = (
        ('draft', 'Borrador (Cotizando)'),
        ('completed', 'Finalizada (Facturada)'),
    )
    code = models.CharField(max_length=100, unique=True, editable=False, verbose_name="código")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="cliente", related_name='sales')
    sale_type = models.CharField(max_length=3, choices=SALE_TYPE_CHOICES, default='FCF', verbose_name="tipo de documento")
    date = models.DateTimeField(default=timezone.now, verbose_name="fecha")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="sucursal", related_name='sales')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="estado")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False, verbose_name="IVA (13%)")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False, verbose_name="total a pagar")

    # Auditoría
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sale'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-date']

    def __str__(self):
        return f"{self.code} - {self.client} (${self.total})"

    def clean(self):
        if self.sale_type == 'CCF' and not self.client.is_tax_contributor:
            raise ValidationError({'client': "El cliente no aplica para Crédito Fiscal (No es contribuyente)."})
        if self.pk:
            old_status = Sale.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            if old_status == 'completed' and self.status != 'completed':
                raise ValidationError("No se puede modificar una venta ya finalizada.")

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"SLE-{date_str}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="cantidad")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="precio unitario", blank=True, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="descuento (%)")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def row_total(self):
        # (Cantidad * Precio) * (1 - (Descuento / 100))
        subtotal = self.quantity * self.price
        discount_factor = self.discount / Decimal('100.00')
        return subtotal * (Decimal('1.00') - discount_factor)