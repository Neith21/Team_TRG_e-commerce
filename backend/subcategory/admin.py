from django.contrib import admin
from subcategory.models import Subcategory

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = (
        'name',
        'category',
        'active',
        'created_at',
        'modified_by'
    )

    list_filter = ('active', 'category', 'created_by', 'created_at', 'modified_by', 'updated_at')
    search_fields = ('name', 'description', 'category__name', 'created_by__username', 'modified_by__username')
    ordering = ('category__name', 'name')

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'description', 'active')
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