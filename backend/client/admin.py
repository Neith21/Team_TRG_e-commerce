from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('dui', 'full_name', 'phone', 'department', 'municipality', 'is_tax_contributor', 'active')
    list_filter = ('department', 'is_tax_contributor', 'active')
    search_fields = ('first_name', 'last_name', 'dui', 'nrc', 'business_line')
    
    fieldsets = (
        ("Información Personal", {
            'fields': ('first_name', 'last_name', 'dui', 'phone', 'email')
        }),
        ("Ubicación", {
            'fields': ('department', 'municipality', 'address')
        }),
        ("Información Fiscal", {
            'fields': ('is_tax_contributor', 'nrc', 'business_line'),
            'description': "Complete NRC y Giro únicamente si el cliente requiere Crédito Fiscal."
        }),
        ("Auditoría del Sistema", {
            'classes': ('collapse',),
            'fields': ('active', 'created_by', 'created_at', 'modified_by', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_by', 'created_at', 'modified_by', 'updated_at')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Nombre Completo"
    full_name.admin_order_field = 'first_name'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)