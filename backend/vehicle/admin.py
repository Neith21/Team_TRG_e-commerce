from django.contrib import admin
from vehicle.models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'brand', 'model', 'year', 'vehicle_type', 'driver_name', 'max_capacity_kg', 'active')
    list_filter = ('vehicle_type', 'active', 'brand')
    search_fields = ('plate', 'driver_name', 'brand', 'model')

    readonly_fields = ('created_at', 'updated_at', 'created_by', 'modified_by')

    fieldsets = (
        ("Datos del Vehículo", {
            'fields': ('plate', 'brand', 'model', 'year', 'vehicle_type', 'max_capacity_kg')
        }),
        ("Conductor y Estado", {
            'fields': ('driver_name', 'description', 'active')
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