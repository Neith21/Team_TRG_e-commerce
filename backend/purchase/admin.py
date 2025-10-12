from django.contrib import admin
from django.utils import timezone
from .models import Purchase
from purchase_detail.models import PurchaseDetail
from buy_order.models import BuyOrder
from django.utils.html import format_html
from django.urls import reverse

class PurchaseDetailInline(admin.TabularInline):
    model = PurchaseDetail
    fields = ('product', 'unit', 'quantity', 'price', 'is_received')
    readonly_fields = ('product', 'unit', 'quantity', 'price')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    # --- Vista de Lista ---
    list_display = ('code', 'invoice_number', 'buy_order', 'provider', 'date', 'prorrateo_asociado', 'is_approved', 'active')
    list_filter = ('is_approved', 'active', 'provider', 'date')
    search_fields = ('code', 'invoice_number', 'buy_order__code', 'provider__name')
    ordering = ('-date',)

    inlines = []

    def has_change_permission(self, request, obj=None):
        """Impide la edición si la compra ya tiene un prorrateo asociado."""
        if obj is not None and hasattr(obj, 'proration'):
            return False  # Deniega el permiso de cambio si existe un prorrateo
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Impide el borrado si la compra ya tiene un prorrateo asociado."""
        if obj is not None and hasattr(obj, 'proration'):
            return False  # Deniega el permiso de borrado si existe un prorrateo
        return super().has_delete_permission(request, obj)

    def prorrateo_asociado(self, obj):
        """Crea un enlace al prorrateo si existe, para dar feedback visual."""
        if hasattr(obj, 'proration'):
            # Genera la URL del admin para ese prorrateo específico
            url = reverse('admin:proration_proration_change', args=[obj.proration.pk])
            return format_html(f'<a href="{url}">{obj.proration.code}</a>')
        return "N/A"
    prorrateo_asociado.short_description = "Prorrateo Asociado"

    def get_readonly_fields(self, request, obj=None):
        base_readonly = ['code', 'provider', 'created_at', 'updated_at', 'created_by', 'modified_by']
        if obj:
            return base_readonly + ['buy_order', 'invoice_number']
        return base_readonly

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "buy_order":
            kwargs["queryset"] = BuyOrder.objects.filter(is_approved=True, purchase__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change and obj.buy_order:
            obj.created_by = request.user
            obj.modified_by = request.user
            obj.provider = obj.buy_order.provider

            super().save_model(request, obj, form, change)
            for detail in obj.buy_order.details.all():
                PurchaseDetail.objects.create(
                    purchase=obj, product=detail.product, unit=detail.unit,
                    quantity=detail.quantity, price=detail.price,
                    created_by=request.user, modified_by=request.user
                )
            return

        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return ((None, {'fields': ('buy_order', 'invoice_number', 'date')}),)
        return (
            ("Información Principal", {
                'fields': ('code', 'invoice_number', 'buy_order', 'provider', 'date', 'is_approved', 'active')
            }),
            ('Información de Auditoría', {
                'classes': ('collapse',),
                'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
            }),
        )

    def get_inline_instances(self, request, obj=None):
        if obj:
            return [PurchaseDetailInline(self.model, self.admin_site)]
        return []