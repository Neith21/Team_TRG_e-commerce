from django.contrib import admin
from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    
    # --- Vista de Lista ---
    list_display = ('name', 'branch_type', 'department', 'municipality', 'phone', 'active')
    list_filter = ('branch_type', 'department', 'active')
    search_fields = ('name', 'municipality', 'address')
    ordering = ('name',)

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        ("Información General", {
            'fields': ('name', 'branch_type', 'phone', 'active')
        }),
        ("Ubicación", {
            'fields': ('department', 'municipality', 'address')
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