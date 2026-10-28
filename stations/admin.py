from django.contrib import admin

from stations.models import Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "capacity", "manager", "is_active")
    list_filter = ("is_active",)
    list_select_related = ("manager",)
    search_fields = ("name", "address")
