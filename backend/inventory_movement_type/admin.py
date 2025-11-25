from django.contrib import admin
from django.utils.html import format_html
from .models import InventoryMovementType

@admin.register(InventoryMovementType)
class InventoryMovementTypeAdmin(admin.ModelAdmin):
    
    # --- Vista de Lista ---
    list_display = ('code', 'name', 'flow_badge', 'active')
    list_filter = ('flow', 'active')
    search_fields = ('name', 'code')
    ordering = ('name',)

    # --- Formulario ---
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        ("Definición del Movimiento", {
            'fields': ('name', 'code', 'flow', 'description', 'active')
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    def flow_badge(self, obj):
        if obj.flow == 'in':
            color = 'green'
            label = 'Entrada (+)'
        else:
            color = 'red'
            label = 'Salida (-)'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )
    flow_badge.short_description = "Flujo"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)