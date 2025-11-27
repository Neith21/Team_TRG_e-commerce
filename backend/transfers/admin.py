from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
import uuid

from .models import Transfer, TransferDetail
from inventory.models import Inventory
from inventory_movement_type.models import InventoryMovementType
from kardex.models import Kardex

class TransferDetailInline(admin.TabularInline):
    model = TransferDetail
    extra = 0
    autocomplete_fields = ['product']

    fields = ('product', 'required_quantity', 'sent_quantity', 'received_quantity', 'comment')

    can_delete = True 

    def get_readonly_fields(self, request, obj=None):
        readonly_always = []
        
        if not obj:
            return ['received_quantity']

        if obj.status == 'picking':
            return ['received_quantity']

        if obj.status == 'transit':
            return [f.name for f in self.model._meta.fields]

        if obj.status == 'received':
            return ['product', 'required_quantity', 'sent_quantity']
            
        return readonly_always

    def has_add_permission(self, request, obj=None):
        if obj and obj.status != 'picking':
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status != 'picking':
            return False
        return True


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('code', 'date', 'source_branch', 'dest_branch', 'status', 'active')
    list_filter = ('status', 'source_branch', 'dest_branch')
    search_fields = ('code', 'source_branch__name')
    
    inlines = [TransferDetailInline]

    fieldsets = (
        ("Datos del Traslado", {
            'fields': ('code', 'status', 'date', 'source_branch', 'dest_branch', 'vehicle')
        }),
        ("Auditoría del Sistema", {
            'classes': ('collapse',),
            'fields': ('active', 'created_by', 'created_at', 'modified_by', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        base_readonly = ['code', 'created_by', 'created_at', 'modified_by', 'updated_at']
        
        if not obj:
            return base_readonly

        if obj.status == 'received':
            operational_readonly = ['status', 'source_branch', 'dest_branch', 'vehicle', 'date']
            return base_readonly + operational_readonly

        if obj.status == 'transit':
            operational_readonly = ['source_branch', 'dest_branch', 'vehicle', 'date']
            return base_readonly + operational_readonly
            
        return base_readonly

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'status' in form.base_fields:
            status_field = form.base_fields['status']

            if not obj:
                status_field.choices = [
                    ('picking', 'En Preparación (Picking)'),
                ]

            elif obj.status == 'picking':
                status_field.choices = [
                    ('picking', 'En Preparación (Picking)'),
                    ('transit', 'En Tránsito'),
                ]

            elif obj.status == 'transit':
                status_field.choices = [
                    ('transit', 'En Tránsito'),
                    ('received', 'Recibida Completa'),
                ]
            
        return form

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status != 'picking':
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user

        old_status = None
        if change:
            old_obj = Transfer.objects.get(pk=obj.pk)
            old_status = old_obj.status
        else:
            old_status = 'picking'

        super().save_model(request, obj, form, change)
        
        if old_status == 'picking' and obj.status == 'transit':
            try:
                with transaction.atomic():
                    self.process_inventory_transfer(request, obj)
            except ValidationError as e:
                messages.set_level(request, messages.ERROR)
                messages.error(request, f"Error al procesar traslado: {e.message}")
                obj.status = 'picking'
                obj.save(update_fields=['status', 'modified_by', 'updated_at'])

        elif old_status == 'transit' and obj.status == 'received':
            pass

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if not instance.pk:
                instance.created_by = request.user

            instance.modified_by = request.user
            instance.active = True
            instance.save()

        for obj in formset.deleted_objects:
            obj.delete()
        
        formset.save_m2m()

    def process_inventory_transfer(self, request, transfer):
        try:
            move_out = InventoryMovementType.objects.get(code='TRANS-OUT')
            move_in = InventoryMovementType.objects.get(code='TRANS-IN')
        except InventoryMovementType.DoesNotExist:
            raise ValidationError("Faltan tipos de movimiento (TRANS-OUT o TRANS-IN).")

        details = transfer.details.filter(active=True)
        if not details.exists():
            raise ValidationError("La transferencia no tiene productos.")

        for detail in details:
            qty_needed = detail.sent_quantity
            if qty_needed <= 0: continue

            source_batches = Inventory.objects.filter(
                branch=transfer.source_branch,
                product=detail.product,
                quantity__gt=0,
                active=True
            ).order_by('created_at')

            total_available = sum(b.quantity for b in source_batches)
            if total_available < qty_needed:
                raise ValidationError(f"Stock insuficiente de '{detail.product}' en origen. Se requieren {qty_needed}, hay {total_available}.")

            qty_remaining = qty_needed

            for batch_record in source_batches:
                if qty_remaining <= 0: break
                to_take = min(batch_record.quantity, qty_remaining)

                batch_record.quantity -= to_take
                batch_record.original_quantity -= to_take
                batch_record.modified_by = request.user
                batch_record.save()

                #Kardex Salida
                Kardex.objects.create(
                    transaction_id=transfer.pk,
                    document_number=transfer.code,
                    movement_type=move_out,
                    inventory_entry=batch_record,
                    branch=transfer.source_branch,
                    product=detail.product,
                    batch=batch_record.batch,
                    quantity=to_take * -1,
                    cost=batch_record.cost,
                    created_by=request.user
                )

                dest_inventory, created = Inventory.objects.get_or_create(
                    branch=transfer.dest_branch,
                    product=detail.product,
                    batch=batch_record.batch,
                    defaults={
                        'entry_number': uuid.uuid4(),
                        'original_quantity': 0,
                        'quantity': 0,
                        'cost': batch_record.cost,
                        'created_by': request.user,
                        'modified_by': request.user,
                        'active': True
                    }
                )

                dest_inventory.quantity += to_take
                dest_inventory.original_quantity += to_take

                if not created:
                    dest_inventory.modified_by = request.user
                
                dest_inventory.save()

                #Kardex Entrada
                Kardex.objects.create(
                    transaction_id=transfer.pk,
                    document_number=transfer.code,
                    movement_type=move_in,
                    inventory_entry=dest_inventory,
                    branch=transfer.dest_branch,
                    product=detail.product,
                    batch=dest_inventory.batch,
                    quantity=to_take,
                    cost=dest_inventory.cost,
                    created_by=request.user
                )

                qty_remaining -= to_take