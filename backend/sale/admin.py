from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal

from .models import Sale, SaleDetail
from inventory.models import Inventory
from inventory_movement_type.models import InventoryMovementType
from kardex.models import Kardex

class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    extra = 0
    fields = ('product', 'quantity', 'price', 'discount', 'row_total_display')
    readonly_fields = ('price', 'row_total_display') 

    def row_total_display(self, obj):
        if obj.pk or (obj.price and obj.quantity):
            p = obj.price if obj.price else Decimal('0.00')
            q = obj.quantity if obj.quantity else Decimal('0.00')
            d = obj.discount if obj.discount else Decimal('0.00')
            total = (q * p) - d
            return f"${total:.2f}"
        return "$0.00"
    row_total_display.short_description = "Subtotal Línea"

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'completed':
            return [f.name for f in self.model._meta.fields] + ['row_total_display']
        return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        return False if obj and obj.status == 'completed' else True

    def has_delete_permission(self, request, obj=None):
        return False if obj and obj.status == 'completed' else True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            try:
                sale_id = request.resolver_match.kwargs.get('object_id')
                if sale_id:
                    sale = Sale.objects.get(pk=sale_id)
                    products_with_stock = Inventory.objects.filter(
                        branch=sale.branch, 
                        quantity__gt=0,
                        active=True
                    ).values_list('product_id', flat=True).distinct()
                    kwargs["queryset"] = db_field.related_model.objects.filter(id__in=products_with_stock)
                else:
                    kwargs["queryset"] = db_field.related_model.objects.none()
            except:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('code', 'date', 'branch', 'client', 'sale_type', 'status', 'total_display')
    list_filter = ('status', 'sale_type', 'branch', 'date')
    search_fields = ('code', 'client__first_name', 'client__dui')
    autocomplete_fields = ['client']
    inlines = [SaleDetailInline]

    fieldsets = (
        ("Encabezado de Venta", {
            'fields': ('code', 'status', 'date', 'branch', 'client', 'sale_type')
        }),
        ("Resumen Financiero", {
            'fields': ('subtotal', 'tax_amount', 'total'),
        }),
        ("Auditoría", {
            'classes': ('collapse',),
            'fields': ('active', 'created_by', 'created_at', 'modified_by'),
        }),
    )

    def total_display(self, obj):
        return f"${obj.total:.2f}"
    total_display.short_description = "Total"

    def get_readonly_fields(self, request, obj=None):
        base = ['code', 'subtotal', 'tax_amount', 'total', 'created_by', 'created_at', 'modified_by']
        if obj and obj.status == 'completed':
            return base + ['status', 'date', 'branch', 'client', 'sale_type']
        return base

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            if 'status' in form.base_fields:
                form.base_fields['status'].choices = [('draft', 'Borrador (Cotizando)')]
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.status = 'draft'
        
        obj.modified_by = request.user
        old_status = 'draft' 
        if change:
            old_status = Sale.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if change and old_status == 'draft' and obj.status == 'completed':
            try:
                with transaction.atomic():
                    self.process_sale_inventory(request, obj)
                    self.calculate_totals(obj)
            except ValidationError as e:
                messages.set_level(request, messages.ERROR)
                messages.error(request, f"Error al facturar: {e.message}")
                Sale.objects.filter(pk=obj.pk).update(status='draft')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        sale = form.instance
        
        for instance in instances:
            if instance.price is None:
                instance.price = Decimal('0.00')

            if sale.status == 'draft':
                oldest_batch = Inventory.objects.filter(
                    branch=sale.branch,
                    product=instance.product,
                    quantity__gt=0,
                    active=True
                ).order_by('created_at').first()

                if oldest_batch:
                    cost = oldest_batch.cost
                    instance.price = cost * Decimal('1.20')
                else:
                    if not instance.price:
                        instance.price = Decimal('0.00')
            
            instance.save()
        
        for obj in formset.deleted_objects:
            obj.delete()
            
        formset.save_m2m()
        
        if sale.status == 'draft':
            self.calculate_totals(sale)

    def calculate_totals(self, sale):
        details = sale.details.all()
        raw_subtotal = sum((d.quantity * d.price) - d.discount for d in details)
        raw_subtotal = Decimal(raw_subtotal)

        tax = Decimal('0.00')
        
        if sale.sale_type == 'CCF':
            tax = raw_subtotal * Decimal('0.13')
            final_total = raw_subtotal + tax
        else:
            final_total = raw_subtotal
            
        Sale.objects.filter(pk=sale.pk).update(
            subtotal=raw_subtotal,
            tax_amount=tax,
            total=final_total
        )

    def process_sale_inventory(self, request, sale):
        try:
            move_sale = InventoryMovementType.objects.get(code='SALE')
        except InventoryMovementType.DoesNotExist:
            raise ValidationError("No existe el tipo de movimiento 'SALE'.")

        details = sale.details.all()
        if not details.exists():
            raise ValidationError("No se puede finalizar una venta sin productos.")

        for detail in details:
            qty_needed = detail.quantity
            if qty_needed <= 0: continue

            batches = Inventory.objects.filter(
                branch=sale.branch,
                product=detail.product,
                quantity__gt=0,
                active=True
            ).order_by('created_at')

            total_available = sum(b.quantity for b in batches)
            if total_available < qty_needed:
                raise ValidationError(f"Stock insuficiente para '{detail.product}'. Requerido: {qty_needed}, Disponible: {total_available}.")

            qty_remaining = qty_needed

            for batch_record in batches:
                if qty_remaining <= 0: break
                
                to_take = min(batch_record.quantity, qty_remaining)

                batch_record.quantity -= to_take
                batch_record.modified_by = request.user
                batch_record.save()

                Kardex.objects.create(
                    transaction_id=sale.pk,
                    document_number=sale.code,
                    movement_type=move_sale,
                    inventory_entry=batch_record,
                    branch=sale.branch,
                    product=detail.product,
                    batch=batch_record.batch,
                    quantity=to_take * -1,
                    cost=batch_record.cost,
                    created_by=request.user
                )

                qty_remaining -= to_take