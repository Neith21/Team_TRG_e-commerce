from django.contrib import admin
from buy_order.models import BuyOrder
from buy_order_detail.models import BuyOrderDetail

class BuyOrderDetailInline(admin.TabularInline):
    model = BuyOrderDetail
    fields = ('product', 'unit', 'quantity', 'price', 'active')
    extra = 1
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

    fieldsets = (
        (None, {
            'fields': ('provider', 'quotation', 'date', 'arrival_date', 'status', 'code')
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    # AQUI IRA EL INLINE AARON
    inlines = [BuyOrderDetailInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    # Nota: El método save_formset es relevante si usas inlines. 
    # Si no tienes un inline para BuyOrder, puedes eliminar este método.
    def save_formset(self, request, form, formset, change):
        for inline_form in formset.forms:
            if inline_form.has_changed() and not inline_form.cleaned_data.get('DELETE', False):
                instance = inline_form.instance
                if not instance.pk:
                    instance.created_by = request.user
                instance.modified_by = request.user
        super().save_formset(request, form, formset, change)
   