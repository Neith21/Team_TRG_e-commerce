from django.contrib import admin
from kardex.models import Kardex

@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'movement_type', 'document_number', 'product', 'branch', 'quantity', 'cost')
    
    list_filter = ('branch', 'movement_type', 'created_at', 'product')
    
    search_fields = ('document_number', 'product__name', 'batch', 'transaction_id')

    # Kardex solo lectura
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False  # No crear registros manuales
    
    def has_change_permission(self, request, obj=None):
        return False  # No actualizar registros manuales
    
    def has_delete_permission(self, request, obj=None):
        return False  # No borrar