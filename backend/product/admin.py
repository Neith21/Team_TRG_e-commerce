from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = (
        'name',
        'code',
        'sku',
        'category',
        'subcategory',
        'active',
    )


    list_filter = ('active', 'category', 'subcategory', 'created_by', 'created_at', 'modified_by', 'updated_at')
    search_fields = ('name', 'description', 'code', 'sku', 'size', 'category__name', 'presentation', 'subcategory__name', 'created_by__username', 'modified_by__username')
    ordering = ('name',)

    # --- Formulario de Edición/Creación ---
    # Campos que son generados automáticamente o de auditoría
    readonly_fields = (
        'uuid', 
        'code', 
        'created_at', 
        'updated_at', 
        'created_by', 
        'modified_by'
    )

    # Organizamos el formulario en secciones lógicas para mayor claridad
    fieldsets = (
        ('Identificadores', {
            'fields': ('sku', 'code', 'uuid')
        }),
        ('Descripción del Producto', {
            'fields': ('name', 'description', 'size', 'presentation')
        }),
        ('Organización', {
            'fields': ('category', 'subcategory')
        }),
        ('Unidades de Medida', {
            'fields': ('purchase_unit', 'sale_unit')
        }),
        ('Estado', {
            'fields': ('active',)
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'modified_by', 'updated_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)