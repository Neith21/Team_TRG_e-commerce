# proration/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Proration, ProrationItem, ProrationExpense
from purchase.models import Purchase

class ProrationItemInline(admin.TabularInline):
    model = ProrationItem
    extra = 0
    
    fields = (
        'product', 
        'quantity', 
        'fob_unit_value', 
        'total_fob_value', 
        'cost_percentage', 
        'prorated_freight',
        'prorated_dai', 
        'prorated_other_expenses',
        'prorated_unit_cost'
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
        'code', 
        'get_provider', 
        'policy_number', 
        'total_fob', 
        'freight', 
        'dai', 
        'total_expenses', 
        'total_prorated_cost'
    )
    inlines = [ProrationItemInline, ProrationExpenseInline]

    def get_readonly_fields(self, request, obj=None):
        base_readonly = (
            'code', 
            'date', 
            'get_provider', 
            'get_origin_country', 
            'total_fob', 
            'freight',
            'dai',
            'get_other_expenses',
            'total_expenses', 
            'total_prorated_cost'
        )
        if obj:
            return base_readonly + ('purchase',)
        return base_readonly

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                ("Seleccionar Compra", {
                    'fields': ('purchase',)
                }),
                ("Documentos de Importación", {
                    'fields': ('import_invoice_number', 'import_invoice_date', 'policy_number', 'policy_date')
                }),
            )
        return (
            ("Información General", {
                'fields': ('code', 'date', 'get_provider', 'get_origin_country', 'purchase')
            }),
            ("Documentos de Importación", {
                'fields': ('import_invoice_number', 'import_invoice_date', 'policy_number', 'policy_date')
            }),
            ("Totales Calculados", {
                'fields': (
                    'total_fob', 
                    'freight',
                    'dai', 
                    'total_expenses', 
                    'total_prorated_cost'
                ), 
                'classes': ('collapse',)
            }),
        )
    
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