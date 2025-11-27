from django.contrib import admin
from django.utils import timezone
from .models import Purchase
from purchase_detail.models import PurchaseDetail
from buy_order.models import BuyOrder
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from inventory.models import Inventory

class PurchaseDetailInline(admin.TabularInline):
    model = PurchaseDetail
    fields = ('product', 'unit', 'quantity', 'verified_quantity', 'price', 'is_received')
    readonly_fields = ('product', 'unit', 'quantity', 'price')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    # --- Vista de Lista ---
    list_display = ('code', 'invoice_number', 'batch', 'buy_order', 'provider', 'date', 'prorrateo_asociado', 'is_approved', 'active')
    list_filter = ('is_approved', 'active', 'provider', 'date')
    search_fields = ('code', 'invoice_number', 'batch', 'buy_order__code', 'provider__name')
    ordering = ('-date',)

    readonly_fields = ('code', 'batch', 'provider', 'created_at', 'updated_at', 'created_by', 'modified_by')

    inlines = []

    actions = ['process_inventory_entry']

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if hasattr(obj, 'proration') or Inventory.objects.filter(batch=obj.batch).exists():
                return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if hasattr(obj, 'proration') or Inventory.objects.filter(batch=obj.batch).exists():
                return False
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
        base_readonly = list(self.readonly_fields)
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

            received_details = obj.buy_order.details.filter(is_received=True, active=True)

            for detail in received_details:
                PurchaseDetail.objects.create(
                    purchase=obj,
                    product=detail.product,
                    unit=detail.unit,
                    quantity=detail.quantity,
                    price=detail.price,
                    active=True,
                    created_by=request.user,
                    modified_by=request.user
                )
            return

        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return ((None, {'fields': ('buy_order', 'invoice_number', 'date')}),)
        return (
            ("Información Principal", {
                'fields': ('code', 'batch', 'invoice_number', 'buy_order', 'provider', 'date', 'is_approved', 'active')
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
    
    @admin.action(description="Procesar Entrada a Inventario")
    def process_inventory_entry(self, request, queryset):
        from inventory.models import Inventory
        from inventory_movement_type.models import InventoryMovementType
        from django.db import transaction
        from kardex.models import Kardex
        from branch.models import Branch

        try:
            movement_type = InventoryMovementType.objects.get(code='PURCHASE')
        except InventoryMovementType.DoesNotExist:
            self.message_user(request, "Error Crítico: No existe el Tipo de Movimiento con código 'PURCHASE'.", level=messages.ERROR)
            return

        target_branch = Branch.objects.filter(active=True).first()
        
        if not target_branch:
            self.message_user(request, "Error Crítico: No hay ninguna SUCURSAL activa registrada en el sistema.", level=messages.ERROR)
            return
            
        TARGET_BRANCH_ID = target_branch.pk

        success_count = 0
        
        for purchase in queryset:
            if not purchase.is_approved:
                self.message_user(request, f"Omitido {purchase.code}: La compra no está aprobada.", level=messages.WARNING)
                continue

            if Inventory.objects.filter(batch=purchase.batch).exists():
                self.message_user(request, f"Omitido {purchase.code}: Ya fue ingresada al inventario anteriormente.", level=messages.WARNING)
                continue

            try:
                with transaction.atomic():
                    valid_details = purchase.details.filter(verified_quantity__gt=0)
                    
                    if not valid_details.exists():
                        self.message_user(request, f"Omitido {purchase.code}: No tiene detalles con 'Cantidad Verificada' mayor a 0.", level=messages.WARNING)
                        continue

                    for detail in valid_details:
                        inv_entry = Inventory.objects.create(
                            branch_id=TARGET_BRANCH_ID,
                            product=detail.product,
                            batch=purchase.batch,
                            original_quantity=detail.verified_quantity,
                            quantity=detail.verified_quantity,
                            cost=detail.price,
                            created_by=request.user,
                            modified_by=request.user
                        )
                        Kardex.objects.create(
                            transaction_id=purchase.pk,
                            document_number=purchase.invoice_number,
                            movement_type=movement_type,
                            inventory_entry=inv_entry,
                            branch_id=TARGET_BRANCH_ID,
                            product=detail.product,
                            batch=purchase.batch,
                            quantity=detail.verified_quantity,
                            cost=detail.price,
                            created_by=request.user
                        )
                    
                    success_count += 1
            
            except Exception as e:
                self.message_user(request, f"Error al procesar {purchase.code}: {str(e)}", level=messages.ERROR)

        if success_count > 0:
            self.message_user(request, f"Exéxito: Se procesaron {success_count} compras al inventario.", level=messages.SUCCESS)