from django.urls import path

from vehicles import views

app_name = "vehicles"

urlpatterns = [
    path("", views.vehicle_list, name="vehicle_list"),
    path("<int:vehicle_id>/", views.vehicle_detail, name="vehicle_detail"),
    path(
        "<int:vehicle_id>/station/<int:station_id>/",
        views.vehicle_station,
        name="vehicle_station",
    ),
    path("<int:vehicle_id>/rental/start/", views.vehicle_rental_start, name="vehicle_rental_start"),
    path("<int:vehicle_id>/rental/end/", views.vehicle_rental_end, name="vehicle_rental_end"),
    path("<int:vehicle_id>/battery/", views.vehicle_battery, name="vehicle_battery"),
    path("<int:vehicle_id>/maintenance/", views.vehicle_maintenance, name="vehicle_maintenance"),
    path(
        "<int:vehicle_id>/maintenance/return/",
        views.vehicle_maintenance_return,
        name="vehicle_maintenance_return",
    ),
]
