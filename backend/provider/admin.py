from django.contrib import admin
from .models import Provider
from provider_contact.models import ProviderContact

class ProviderContactInline(admin.TabularInline):

    model = ProviderContact
    fields = ('first_name', 'last_name', 'phone', 'email', 'active')
    extra = 1
    can_delete = True

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    # --- Vista de Lista ---
    list_display = ('name', 'country', 'phone', 'email', 'active')
    list_filter = ('active', 'country')
    search_fields = ('name', 'email', 'phone', 'contacts__first_name', 'contacts__last_name')
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

    inlines = [ProviderContactInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for inline_form in formset.forms:
            if inline_form.has_changed() and not inline_form.cleaned_data.get('DELETE', False):
                instance = inline_form.instance
                if not instance.pk:
                    instance.created_by = request.user
                instance.modified_by = request.user
        super().save_formset(request, form, formset, change)