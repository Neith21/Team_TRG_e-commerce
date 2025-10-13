from django.contrib import admin
from django.contrib import messages
from .models import Proration, ProrationItem, ProrationExpense
from purchase.models import Purchase

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
        'code', 'get_provider', 'policy_number', 'total_fob', 
        'freight', 'dai', 'total_expenses', 'total_prorated_cost'
    )
    inlines = [ProrationItemInline, ProrationExpenseInline]
    actions = ['run_proration_action']

    def get_readonly_fields(self, request, obj=None):
        base_readonly = (
            'code', 'date', 'get_provider', 'get_origin_country', 
            'total_fob', 'freight', 'dai', 'total_expenses', 'total_prorated_cost'
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
            ("Información General", {'fields': ('code', 'date', 'get_provider', 'get_origin_country', 'purchase')}),
            ("Documentos de Importación (Opcional)", {'fields': ('import_invoice_number', 'import_invoice_date', 'policy_number', 'policy_date')}),
            ("Totales Calculados", {
                'fields': ('total_fob', 'freight', 'dai', 'total_expenses', 'total_prorated_cost'), 
                'classes': ('collapse',)
            }),
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
        is_new = not change
        super().save_model(request, obj, form, change)

        if is_new and obj.purchase:
            for detail in obj.purchase.details.all():
                ProrationItem.objects.create(
                    proration=obj, 
                    product=detail.product, 
                    quantity=detail.quantity, 
                    fob_unit_value=detail.price
                )
            obj.run_proration()
            messages.success(request, f"Prorrateo creado y calculado exitosamente. Costo total: ${obj.total_prorated_cost}")

    def save_related(self, request, form, formsets, change):
        """Se ejecuta después de guardar los inlines (gastos)"""
        super().save_related(request, form, formsets, change)
        if form.instance and form.instance.pk:
            form.instance.run_proration()
            messages.info(request, "Prorrateo recalculado automáticamente.")

    def get_provider(self, obj):
        if obj.purchase: 
            return obj.purchase.provider.name
        return "N/A"
    get_provider.short_description = 'Proveedor'

    def get_origin_country(self, obj):
        if obj.purchase: 
            return obj.purchase.provider.country
        return "N/A"
    get_origin_country.short_description = 'País de Origen'
        
    @admin.action(description="Ejecutar Prorrateo de Costos (Manual)")
    def run_proration_action(self, request, queryset):
        count = 0
        for proration in queryset:
            proration.run_proration()
            count += 1
        self.message_user(
            request, 
            f"Se recalculó el prorrateo para {count} registro(s).",
            messages.SUCCESS
        )