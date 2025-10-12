from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Quotation
from quotation_detail.models import QuotationDetail

class QuotationDetailInline(admin.TabularInline):
    model = QuotationDetail
    fields = ('product', 'unit', 'required_quantity', 'price', 'approved_quantity', 'is_approved', 'active')
    extra = 1
    can_delete = True

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = ('code', 'provider', 'date', 'is_approved', 'orden_de_compra_asociada', 'active') # Campo nuevo
    list_filter = ('is_approved', 'active', 'provider', 'date')
    search_fields = ('code', 'provider__name')
    ordering = ('-date',)

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('code', 'created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('provider', 'date', 'is_approved', 'active', 'code')
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    inlines = [QuotationDetailInline]

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.purchase_orders.exists():
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.purchase_orders.exists():
            return False
        return super().has_delete_permission(request, obj)

    def orden_de_compra_asociada(self, obj):
        buy_order = obj.purchase_orders.first()
        if buy_order:
            url = reverse('admin:buy_order_buyorder_change', args=[buy_order.pk])
            return format_html(f'<a href="{url}">{buy_order.code}</a>')
        return "N/A"
    orden_de_compra_asociada.short_description = "Orden de Compra"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for inline_form in formset.forms:
            if inline_form.has_changed() and not inline_form.cleaned_data.get('DELETE', False):
                instance = inline_form.instance
                if not instance.pk:
                    instance.created_by = request.user
                instance.modified_by = request.user
        super().save_formset(request, form, formset, change)