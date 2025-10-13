from django.db import models
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from purchase.models import Purchase
from product.models import Product
from django.conf import settings

class Proration(models.Model):
    purchase = models.OneToOneField(Purchase, on_delete=models.PROTECT, verbose_name="Compra a Prorratear", help_text="Seleccione la compra aprobada que desea prorratear.", null=True, blank=True)
    code = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Código de Prorrateo")
    date = models.DateField(default=timezone.now, editable=False, verbose_name="Fecha de Creación")
    import_invoice_number = models.CharField(max_length=100, verbose_name="Factura de Importación", null=True, blank=True)
    import_invoice_date = models.DateField(verbose_name="Fecha de Factura", null=True, blank=True)
    policy_number = models.CharField(max_length=100, verbose_name="Póliza", null=True, blank=True)
    policy_date = models.DateField(verbose_name="Fecha de Póliza", null=True, blank=True)
    total_fob = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Total FOB")
    freight = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Flete")
    dai = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="DAI (Aranceles)")
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Total Gastos al Costo")
    total_prorated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Costo Total Prorrateado")

    active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"PRO-{date_str}-{self.pk:05d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    def calculate_totals(self):
        # Calcular total FOB desde los items
        self.total_fob = self.items.aggregate(
            total=Sum(models.F('quantity') * models.F('fob_unit_value'))
        )['total'] or Decimal('0.0')
        
        # Calcular gastos
        expenses_to_include = self.expenses.filter(include_in_proration=True)
        self.freight = expenses_to_include.filter(expense_type='FREIGHT').aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
        self.dai = expenses_to_include.filter(expense_type='DAI').aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
        self.total_expenses = expenses_to_include.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
        self.total_prorated_cost = self.total_fob + self.total_expenses
        self.save()

    def run_proration(self):
        self.calculate_totals()
        
        if self.total_fob <= 0:
            return

        # Calcular factores de prorrateo
        freight_factor = self.freight / self.total_fob
        dai_factor = self.dai / self.total_fob
        other_expenses = self.total_expenses - self.freight - self.dai
        other_factor = other_expenses / self.total_fob

        # Aplicar prorrateo a cada item
        for item in self.items.all():
            # Calcular valor FOB total del item
            item.total_fob_value = item.quantity * item.fob_unit_value
            
            # Calcular porcentaje de participación
            item.cost_percentage = (item.total_fob_value / self.total_fob) * Decimal('100.0')
            
            # Prorratear gastos
            item.prorated_freight = item.total_fob_value * freight_factor
            item.prorated_dai = item.total_fob_value * dai_factor
            item.prorated_other_expenses = item.total_fob_value * other_factor
            
            # Calcular costo total del item
            total_item_cost = (
                item.total_fob_value + 
                item.prorated_freight + 
                item.prorated_dai + 
                item.prorated_other_expenses
            )
            
            # Calcular costo unitario prorrateado
            if item.quantity > 0:
                item.prorated_unit_cost = total_item_cost
            else:
                item.prorated_unit_cost = Decimal('0.0')
            
            item.save()
            
    class Meta:
        verbose_name = "Prorrateo de Importación"
        verbose_name_plural = "Prorrateos de Importación"
        ordering = ['-date']

class ProrationExpense(models.Model):
    EXPENSE_TYPES = [
        ('FREIGHT', 'Flete'), 
        ('DAI', 'DAI (Derechos Arancelarios)'), 
        ('OTHER', 'Otro Gasto')
    ]
    proration = models.ForeignKey(Proration, on_delete=models.CASCADE, related_name="expenses")
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPES, default='OTHER', verbose_name="Tipo de Gasto")
    description = models.CharField(max_length=255, verbose_name="Descripción del Gasto")
    date = models.DateField(verbose_name="Fecha")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    include_in_proration = models.BooleanField(default=True, verbose_name="Incluir en Prorrateo", help_text="Desmarque esta casilla si este gasto no debe afectar el costo del producto.")

    active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} (${self.amount})"
        
    class Meta:
        verbose_name = "Gasto de Importación (Bitácora)"
        verbose_name_plural = "Gastos de Importación (Bitácora)"

class ProrationItem(models.Model):
    proration = models.ForeignKey(Proration, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    fob_unit_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor FOB Unitario")
    cost_percentage = models.DecimalField(max_digits=8, decimal_places=4, default=0.0, editable=False, verbose_name="% de Participación")
    total_fob_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Valor FOB Total")
    prorated_freight = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Flete Prorrateado")
    prorated_dai = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="DAI Prorrateado")
    prorated_other_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, editable=False, verbose_name="Otros Gastos Prorrateados")
    prorated_unit_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0.0, editable=False, verbose_name="Costo Unitario Prorrateado")

    active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} en {self.proration.code}"
    
    class Meta:
        verbose_name = "Ítem de Prorrateo"
        verbose_name_plural = "Ítems de Prorrateo"