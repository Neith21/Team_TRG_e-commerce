from django.contrib import admin
from price_history.models import PriceHistory

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'sale_price', 'is_active', 'start_date')
    list_filter = ('product__category', 'is_active', 'product')
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('analysis_detail', 'product', 'sale_price', 'start_date', 'created_by', 'created_at', 'modified_by', 'updated_at')

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
