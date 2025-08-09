from django.contrib import admin
from buy_order.models import BuyOrder
from buy_order_detail.models import BuyOrderDetail
from quotation_detail.models import QuotationDetail
from django import forms
from quotation.models import Quotation
from .models import BuyOrder

# Configuración de filtros
class BuyOrderForm(forms.ModelForm):
    class Meta:
        model = BuyOrder
        fields = ['provider', 'quotation', 'date', 'arrival_date', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtro para traer únicamente las cotizaciones aprobadas
        qs = Quotation.objects.filter(is_approved=True)
        # Filtro de cotizaciones basado en el proveedor
        if self.data.get('provider'):
            try:
                provider_id = int(self.data.get('provider'))
                qs = qs.filter(provider_id=provider_id)
            except (TypeError, ValueError):
                pass
        elif self.instance.pk and self.instance.provider_id:
            qs = qs.filter(provider_id=self.instance.provider_id)
        else:
            qs = qs.none()
        self.fields['quotation'].queryset = qs
        if qs.count() == 0:
            self.fields['quotation'].help_text = "Hay que seleccionar un proveedor y guardar primero"

class BuyOrderDetailInline(admin.TabularInline):
    model = BuyOrderDetail
    fields = ('product', 'unit', 'quantity', 'price', 'active')
    extra = 0
    can_delete = True

@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = ('code', 'provider', 'quotation', 'date', 'arrival_date', 'status')
    list_filter = ('status', 'provider', 'quotation', 'date')
    search_fields = ('code', 'provider__name', 'quotation__code')
    ordering = ('-date',)

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('code', 'created_at', 'updated_at', 'created_by', 'modified_by')
    form = BuyOrderForm

    fieldsets = (
        (None, {
            'fields': ('provider', 'quotation', 'date', 'arrival_date', 'status', 'code')
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    inlines = [BuyOrderDetailInline]

    def save_model(self, request, obj, form, change):
        creating = obj.pk is None
        if creating:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

        # Heredación de detalles de cotización
        if creating and obj.quotation_id:
            approved_items = QuotationDetail.objects.filter(quotation=obj.quotation, is_approved=True, active=True)
            bulk = []
            for qd in approved_items:
                bulk.append(BuyOrderDetail(
                    buy_order=obj,
                    product=qd.product,
                    unit=qd.unit,
                    price=qd.price,
                    quantity=qd.approved_quantity or qd.required_quantity,
                    active=True,
                    created_by=request.user,
                    modified_by=request.user,
                ))
            if bulk:
                BuyOrderDetail.objects.bulk_create(bulk)

    def save_formset(self, request, form, formset, change):
        for inline_form in formset.forms:
            if inline_form.has_changed() and not inline_form.cleaned_data.get('DELETE', False):
                instance = inline_form.instance
                if not instance.pk:
                    instance.created_by = request.user
                instance.modified_by = request.user
        super().save_formset(request, form, formset, change)


