from django.contrib import admin
from provider_contact.models import ProviderContact

@admin.register(ProviderContact)
class ProviderContactAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = (
        'first_name',
        'last_name',
        'provider',
        'phone',
        'email',
        'active'
    )
    list_filter = ('active', 'provider', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'provider__name')
    ordering = ('provider__name', 'first_name')

    # --- Formulario de Edición/Creación ---
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        (None, {
            'fields': ('provider', 'first_name', 'last_name', 'phone', 'email', 'active')
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