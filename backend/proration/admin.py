from django.contrib import admin
from django.contrib import messages
from .models import Proration, ProrationItem, ProrationExpense
from purchase.models import Purchase
from django.utils.html import format_html
from django.urls import reverse

class ProrationItemInline(admin.TabularInline):
    model = ProrationItem
    extra = 0
    fields = (
        'product', 'quantity', 'fob_unit_value', 'total_fob_value', 
        'cost_percentage', 'prorated_freight', 'prorated_dai', 
        'prorated_other_expenses', 'prorated_unit_cost'
    )
    readonly_fields = fields
    def has_add_permission(self, request, obj):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class ProrationExpenseInline(admin.TabularInline):
    model = ProrationExpense
    extra = 1
    fields = ('expense_type', 'description', 'date', 'amount', 'include_in_proration')

@admin.register(Proration)
class ProrationAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'get_provider', 'policy_number', 'is_approved', 'analisis_asociado',
        'total_fob', 'active'
    )
    inlines = [ProrationItemInline, ProrationExpenseInline]
    actions = ['run_proration_action']

    def has_change_permission(self, request, obj=None):
        if obj is not None and hasattr(obj, 'priceanalysis'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and hasattr(obj, 'priceanalysis'):
            return False
        return super().has_delete_permission(request, obj)
    
    def analisis_asociado(self, obj):
        if hasattr(obj, 'priceanalysis'):
            url = reverse('admin:price_analysis_priceanalysis_change', args=[obj.priceanalysis.pk])
            return format_html(f'<a href="{url}">{obj.priceanalysis.code}</a>')
        return "Disponible"
    analisis_asociado.short_description = 'Análisis Asociado'

    def get_readonly_fields(self, request, obj=None):
        base_readonly = (
            'code', 'date', 'get_provider', 'get_origin_country', 'total_fob', 
            'freight', 'dai', 'total_expenses', 'total_prorated_cost',
            'created_by', 'created_at', 'modified_by', 'updated_at'
        )
        if obj:
            return base_readonly + ('purchase',)
        return base_readonly

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                ("Seleccionar Compra", {'fields': ('purchase',)}),
                ("Documentos de Importación (Opcional)", {'fields': ('import_invoice_number', 'import_invoice_date', 'policy_number', 'policy_date')}),
            )
        return (
            ("Información General", {'fields': ('code', 'date', 'get_provider', 'get_origin_country', 'purchase', 'is_approved', 'active')}),
            ("Documentos de Importación (Opcional)", {'fields': ('import_invoice_number', 'import_invoice_date', 'policy_number', 'policy_date')}),
            ("Totales Calculados", {'fields': ('total_fob', 'freight', 'dai', 'total_expenses', 'total_prorated_cost'), 'classes': ('collapse',)}),
            ("Auditoría", {'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'), 'classes': ('collapse',)}),
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "purchase":
            queryset = Purchase.objects.filter(is_approved=True, proration__isnull=True)
            if 'object_id' in request.resolver_match.kwargs:
                try:
                    proration_id = request.resolver_match.kwargs['object_id']
                    current_purchase = Proration.objects.get(pk=proration_id).purchase
                    if current_purchase:
                        queryset = queryset | Purchase.objects.filter(pk=current_purchase.pk)
                except Proration.DoesNotExist:
                    pass
            kwargs["queryset"] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
        
        if not change and obj.purchase:
            received_details = obj.purchase.details.filter(is_received=True, active=True)

            items_created_count = 0
            items_skipped_count = 0

            for detail in received_details:

                qty_to_use = detail.verified_quantity

                if qty_to_use > 0:
                    ProrationItem.objects.create(
                        proration=obj,
                        product=detail.product,
                        quantity=qty_to_use,
                        fob_unit_value=detail.price,
                        created_by=request.user,
                        modified_by=request.user
                    )
                    items_created_count += 1
                else:
                    items_skipped_count += 1
            obj.run_proration()

            if items_skipped_count > 0:
                messages.warning(
                    request, 
                    f"Atención: Se omitieron {items_skipped_count} productos del prorrateo porque su 'Cantidad Verificada' era 0."
                )
            
            if items_created_count == 0:
                messages.error(
                    request, 
                    "Error: No se agregaron items al prorrateo. Verifique que haya ingresado las cantidades verificadas en la Compra."
                )

    def save_related(self, request, form, formsets, change):
        """Se ejecuta después de guardar los inlines (gastos)"""
        for formset in formsets:
            for inline_form in formset.forms:
                if inline_form.has_changed():
                    instance = inline_form.instance
                    if not instance.pk:
                        instance.created_by = request.user
                    instance.modified_by = request.user
        
        super().save_related(request, form, formsets, change)
        if form.instance and form.instance.pk:
            form.instance.run_proration()
            messages.info(request, "Prorrateo recalculado automáticamente.")

    def get_provider(self, obj):
        if obj.purchase: return obj.purchase.provider.name
        return "N/A"
    get_provider.short_description = 'Proveedor'

    def get_origin_country(self, obj):
        if obj.purchase: return obj.purchase.provider.country
        return "N/A"
    get_origin_country.short_description = 'País de Origen'
        
    @admin.action(description="Ejecutar Prorrateo de Costos (Manual)")
    def run_proration_action(self, request, queryset):
        count = 0
        for proration in queryset:
            proration.run_proration()
            proration.modified_by = request.user
            proration.save()
            count += 1
        self.message_user(request, f"Se recalculó el prorrateo para {count} registro(s).")