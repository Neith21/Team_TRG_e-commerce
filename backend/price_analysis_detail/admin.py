from django.contrib import admin
from price_history.models import PriceHistory, ActivePrice

@admin.register(ActivePrice)
class ActivePriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'sale_price', 'start_date', 'get_analysis_code')
    list_filter = ('product__category',)
    search_fields = ('product__name', 'product__sku')
    
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return PriceHistory.objects.filter(is_active=True)

    def get_analysis_code(self, obj):
        return obj.analysis_detail.analysis.code
    get_analysis_code.short_description = 'Código de Análisis de Origen'