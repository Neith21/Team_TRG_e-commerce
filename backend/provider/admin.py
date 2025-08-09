from django.contrib import admin
from provider.models import Provider

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = (
        'name',
        'country',
        'phone',
        'email',
        'active'
    )
    list_filter = ('active', 'country', 'created_at', 'updated_at')
    search_fields = ('name', 'country', 'email', 'phone')
    ordering = ('name',)

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('name', 'country', 'address', 'phone', 'email', 'active')
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