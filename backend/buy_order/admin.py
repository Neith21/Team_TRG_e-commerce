from django.contrib import admin
from buy_order.models import BuyOrder
from buy_order_detail.models import BuyOrderDetail
from quotation.models import Quotation
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from .models import BuyOrder
from buy_order_detail.models import BuyOrderDetail

class BuyOrderDetailInline(admin.TabularInline):
    model = BuyOrderDetail
    fields = ('product', 'unit', 'quantity', 'price', 'is_received')
    readonly_fields = ('product', 'unit', 'quantity', 'price')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = ('code', 'provider', 'quotation', 'date', 'compra_asociada', 'is_approved', 'active')
    list_filter = ('is_approved', 'active', 'provider', 'date')
    search_fields = ('code', 'provider__name', 'quotation__code')
    ordering = ('-date',)

    # --- Formulario de Edición/Creación ---
    fieldsets = (
        ("Crear desde Cotización", {
            'fields': ('quotation', 'arrival_date'),
            'description': 'Al crear, seleccione una cotización. El proveedor, la fecha y los detalles se llenarán automáticamente.'
        }),
        ("Información de la Orden", {
            'fields': ('provider', 'date', 'is_approved', 'active', 'code')
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    inlines = []

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.purchase.exists():
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.purchase.exists():
            return False
        return super().has_delete_permission(request, obj)

    def compra_asociada(self, obj):
        purchase = obj.purchase.first()
        if purchase:
            url = reverse('admin:purchase_purchase_change', args=[purchase.pk])
            return format_html(f'<a href="{url}">{purchase.invoice_number}</a>')
        return "N/A"
    compra_asociada.short_description = "Nº Factura Compra"

    def get_readonly_fields(self, request, obj=None):
        base_readonly = ['code', 'provider', 'created_at', 'updated_at', 'created_by', 'modified_by']
        if obj:
            return base_readonly + ['quotation']
        return base_readonly
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "quotation":
            # Muestra solo cotizaciones aprobadas que no tengan ya una orden de compra asociada
            kwargs["queryset"] = Quotation.objects.filter(is_approved=True, purchase_orders__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user

        if not change and obj.quotation:
            obj.provider = obj.quotation.provider
            obj.date = timezone.now().date()
            super().save_model(request, obj, form, change)

            # Copia los detalles aprobados de la cotización a la nueva orden
            approved_details = obj.quotation.details.filter(is_approved=True, active=True)
            for detail in approved_details:
                BuyOrderDetail.objects.create(
                    buy_order=obj,
                    product=detail.product,
                    unit=detail.unit,
                    price=detail.price,
                    quantity=detail.approved_quantity,
                    is_received=False,
                    active=True,
                    created_by=request.user,
                    modified_by=request.user
                )
            return
        super().save_model(request, obj, form, change)

    # Muestra el inline solo cuando se edita una orden ya creada
    def get_inline_instances(self, request, obj=None):
        if obj:
            return [BuyOrderDetailInline(self.model, self.admin_site)]
        return []

    # Oculta el campo de proveedor al crear, ya que es automático
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:
            return (fieldsets[0], fieldsets[2])
        return fieldsets