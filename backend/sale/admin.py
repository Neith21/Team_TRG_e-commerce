from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import path
from decimal import Decimal
from django import forms

from .models import Sale, SaleDetail
from inventory.models import Inventory
from inventory_movement_type.models import InventoryMovementType
from kardex.models import Kardex

class SaleDetailForm(forms.ModelForm):
    class Meta:
        model = SaleDetail
        fields = '__all__'
        widgets = {
            'price': forms.NumberInput(attrs={
                'readonly': 'readonly', 
                'style': 'background-color: #f8f9fa; cursor: not-allowed; width: 80px;'
            }),
            'discount': forms.NumberInput(attrs={
                'placeholder': '0%',
                'style': 'width: 60px;'
            }),
            'quantity': forms.NumberInput(attrs={
                'style': 'width: 60px;'
            }),
        }

class SaleDetailInline(admin.TabularInline):
    model = SaleDetail
    form = SaleDetailForm
    extra = 1
    fields = ('product', 'quantity', 'price', 'discount', 'row_total_display')
    readonly_fields = ('row_total_display',) 

    def row_total_display(self, obj):
        p = obj.price if obj.price else Decimal('0.00')
        q = obj.quantity if obj.quantity else Decimal('0.00')
        d_percent = obj.discount if obj.discount else Decimal('0.00')
        
        subtotal = q * p
        discount_amount = subtotal * (d_percent / Decimal('100'))
        total = subtotal - discount_amount
        return f"${total:.2f}"
    
    row_total_display.short_description = "Subtotal"

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'completed':
            return [f.name for f in self.model._meta.fields] + ['row_total_display']
        return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        return False if obj and obj.status == 'completed' else True

    def has_delete_permission(self, request, obj=None):
        return False if obj and obj.status == 'completed' else True

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

    class Media:
        js = ('admin/js/sale_dynamic.js',)

    def total_display(self, obj):
        return f"${obj.total:.2f}"
    total_display.short_description = "Total"

    def get_readonly_fields(self, request, obj=None):
        base = ['code', 'subtotal', 'tax_amount', 'total', 'created_by', 'created_at', 'modified_by']
        if obj and obj.status == 'completed':
            return base + ['status', 'date', 'branch', 'client', 'sale_type']
        return base

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'completed':
            return False
        return super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['status'].initial = 'completed'
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-products-by-branch/', self.admin_site.admin_view(self.get_products_by_branch), name='sale_get_products'),
            path('get-product-price/', self.admin_site.admin_view(self.get_product_price), name='sale_get_price'),
        ]
        return custom_urls + urls

    def get_products_by_branch(self, request):
        branch_id = request.GET.get('branch_id')
        if not branch_id: return JsonResponse({'products': []})
        products = Inventory.objects.filter(branch_id=branch_id, quantity__gt=0, active=True)\
            .select_related('product').values('product__id', 'product__name', 'product__code').distinct()
        return JsonResponse({'products': [{'id': p['product__id'], 'name': f"{p['product__code']} - {p['product__name']}"} for p in products]})

    def get_product_price(self, request):
        branch_id = request.GET.get('branch_id')
        product_id = request.GET.get('product_id')
        if not branch_id or not product_id: return JsonResponse({'price': '0.00'})
        
        oldest_batch = Inventory.objects.filter(
            branch_id=branch_id, 
            product_id=product_id, 
            quantity__gt=0, 
            active=True
        ).order_by('created_at').first()
        
        if oldest_batch:
            price = oldest_batch.cost * Decimal('1.20') 
            price = price.quantize(Decimal('0.01'))
            return JsonResponse({'price': str(price)})
            
        return JsonResponse({'price': '0.00'})

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        
        if change:
            obj._old_status = Sale.objects.get(pk=obj.pk).status
        else:
            obj._old_status = 'draft'

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        price_map = {}
        for instance in instances:
            if instance.pk:
                price_map[instance.pk] = instance.price
            if instance.price is None: 
                instance.price = Decimal('0.00')
            instance.save()

        for instance in instances:
            if instance.pk in price_map and price_map[instance.pk]:
                instance.price = price_map[instance.pk]
                instance.save(update_fields=['price'])
        
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        obj = form.instance
        old_status = getattr(obj, '_old_status', 'draft')

        if obj.status == 'completed' and (not change or old_status == 'draft'):
            try:
                with transaction.atomic():
                    self.process_sale_inventory(request, obj)
                    self.calculate_totals(obj)
                
                self.message_user(request, f"Venta {obj.code} finalizada y descontada.", level=messages.SUCCESS)
            
            except ValidationError as e:
                Sale.objects.filter(pk=obj.pk).update(status='draft')
                self.message_user(request, f"Error al finalizar venta: {e.message}", level=messages.ERROR)
        
        elif obj.status == 'draft':
            self.calculate_totals(obj)

    def calculate_totals(self, sale):
        details = sale.details.all()
        raw_subtotal = Decimal('0.00') 
        for d in details:
            line_sub = d.quantity * d.price
            discount_amount = line_sub * (d.discount / Decimal('100.00'))
            raw_subtotal += (line_sub - discount_amount)

        tax = Decimal('0.00')
        if sale.sale_type == 'CCF':
            tax = raw_subtotal * Decimal('0.13')
            final_total = raw_subtotal
        else:
            final_total = raw_subtotal
            
        Sale.objects.filter(pk=sale.pk).update(subtotal=raw_subtotal, tax_amount=tax, total=final_total)

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
            total_money_value_extracted = Decimal('0.00')

            for batch_record in batches:
                if qty_remaining <= 0: break

                current_batch_sale_price = batch_record.cost * Decimal('1.20')
                
                to_take = min(batch_record.quantity, qty_remaining)

                total_money_value_extracted += (to_take * current_batch_sale_price)

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

            final_unit_price = total_money_value_extracted / detail.quantity
            final_unit_price = final_unit_price.quantize(Decimal('0.01'))

            SaleDetail.objects.filter(pk=detail.pk).update(price=final_unit_price)