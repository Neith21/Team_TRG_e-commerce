from django.contrib import admin
from .models import PriceAnalysis
from price_analysis_detail.models import PriceAnalysisDetail
from price_history.models import PriceHistory
from proration.models import Proration

class PriceAnalysisDetailInline(admin.TabularInline):
    model = PriceAnalysisDetail
    extra = 0
    fields = ('product', 'quantity', 'invoice_cost', 'final_prorated_cost', 'utility', 'calculated_sale_price')
    readonly_fields = ('product', 'quantity', 'invoice_cost', 'final_prorated_cost', 'calculated_sale_price')

    def calculated_sale_price(self, obj):
        return f"${obj.sale_price:.2f}"
    calculated_sale_price.short_description = "Precio de Venta (Calculado)"
    
    def has_add_permission(self, request, obj):
        return False

@admin.register(PriceAnalysis)
class PriceAnalysisAdmin(admin.ModelAdmin):
    list_display = ('code', 'invoice_number', 'proration', 'date', 'is_approved', 'active')
    inlines = [PriceAnalysisDetailInline]
    actions = ['approve_and_generate_prices']

    def get_readonly_fields(self, request, obj=None):
        base_readonly = ('code', 'date', 'invoice_number', 'created_by', 'created_at', 'modified_by', 'updated_at')
        if obj:
            return base_readonly + ('proration',)
        return base_readonly

    def get_fieldsets(self, request, obj=None):
        base_fields = (
            ("Información Principal", {
                'fields': ('proration', 'is_approved', 'active')
            }),
            ("Documentos de Referencia", {
                'fields': ('code', 'date', 'invoice_number')
            }),
        )
        if obj:
            base_fields += (
                ("Auditoría", {
                    'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return base_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "proration":
            queryset = Proration.objects.filter(is_approved=True, priceanalysis__isnull=True)

            if 'object_id' in request.resolver_match.kwargs:
                try:
                    analysis_id = request.resolver_match.kwargs['object_id']
                    current_proration = PriceAnalysis.objects.get(pk=analysis_id).proration
                    if current_proration:
                        queryset = queryset | Proration.objects.filter(pk=current_proration.pk)
                except (KeyError, PriceAnalysis.DoesNotExist):
                    pass
            
            kwargs["queryset"] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

        if not change:
            for item in obj.proration.items.all():
                PriceAnalysisDetail.objects.create(
                    analysis=obj,
                    product=item.product,
                    quantity=item.quantity,
                    invoice_cost=item.total_fob_value,
                    final_prorated_cost=item.prorated_unit_cost,
                    created_by=request.user,
                    modified_by=request.user
                )

    def save_formset(self, request, form, formset, change):
        for inline_form in formset.forms:
            if inline_form.has_changed():
                instance = inline_form.instance
                instance.modified_by = request.user
        super().save_formset(request, form, formset, change)
    
    @admin.action(description="Aprobar y generar precios en el historial")
    def approve_and_generate_prices(self, request, queryset):
        for analysis in queryset:
            analysis.is_approved = True
            analysis.modified_by = request.user
            analysis.save()
            for detail in analysis.details.all():
                PriceHistory.objects.create(
                    analysis_detail=detail,
                    product=detail.product,
                    sale_price=detail.sale_price,
                    created_by=request.user,
                    modified_by=request.user
                )
        self.message_user(request, "Los precios han sido aprobados y generados en el historial exitosamente.")