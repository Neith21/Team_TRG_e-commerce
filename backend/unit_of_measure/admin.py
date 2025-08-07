from django.contrib import admin
from .models import UnitOfMeasure

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = (
        'name',
        'type',
        'active',
        'created_by',
        'created_at',
        'modified_by',
        'updated_at'
    )

    list_filter = ('active', 'type', 'active', 'created_by', 'created_at', 'modified_by', 'updated_at')
    search_fields = ('name', 'type', 'created_by__username', 'modified_by__username')
    ordering = ('name', 'type')

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'active')
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