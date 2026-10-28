from django.contrib import admin

from vehicles.models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "type", "status", "battery_level", "station")
    list_filter = ("type", "status")
    list_select_related = ("station",)
    search_fields = ("serial_number",)
