import uuid
from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from branch.models import Branch
from inventory.models import Inventory
from kardex.models import Kardex
from inventory_movement_type.models import InventoryMovementType

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'branch', 'short_batch', 'quantity', 'original_quantity', 'cost', 'created_at')
    list_filter = ('branch', 'product__category', 'created_at')
    search_fields = ('product__name', 'product__code', 'batch', 'entry_number')

    readonly_fields = ('entry_number', 'batch', 'original_quantity', 'created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        ("Datos de Ingreso Manual", {
            'fields': ('branch', 'product', 'quantity', 'cost') 
        }),
        ('Auditoría', {
            'classes': ('collapse',),
            'fields': ('entry_number', 'batch', 'active', 'created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    def short_batch(self, obj):
        return str(obj.batch)[:8] + "..."
    short_batch.short_description = "Lote"

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            return

        obj.created_by = request.user
        obj.modified_by = request.user

        if not obj.batch:
            obj.batch = uuid.uuid4()
        obj.original_quantity = obj.quantity

        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
                try:
                    move_type = InventoryMovementType.objects.get(code='ADJ-POS')
                except InventoryMovementType.DoesNotExist:
                    messages.error(request, "No existe el tipo de movimiento 'ADJ-POS'. El Kardex no se generó.")
                    return

                Kardex.objects.create(
                    transaction_id=obj.pk,
                    document_number="AJUSTE MANUAL",
                    movement_type=move_type,
                    inventory_entry=obj,
                    branch=obj.branch,
                    product=obj.product,
                    batch=obj.batch,
                    quantity=obj.quantity,
                    cost=obj.cost,
                    created_by=request.user
                )
                messages.success(request, f"Inventario agregado y registrado en Kardex como Ajuste Manual (Lote: {str(obj.batch)[:8]}).")

        except Exception as e:
            messages.error(request, f"Error al guardar inventario: {str(e)}")
            
    def changelist_view(self, request, extra_context=None):
        if 'branch__id__exact' not in request.GET:
            default_branch = Branch.objects.order_by('id').first()
            if default_branch:
                params = request.GET.copy()
                params['branch__id__exact'] = default_branch.id
                return HttpResponseRedirect(f"{request.path}?{params.urlencode()}")

        return super().changelist_view(request, extra_context)