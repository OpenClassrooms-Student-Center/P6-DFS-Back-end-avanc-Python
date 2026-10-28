from django.urls import path

from stations import views

app_name = "stations"

urlpatterns = [
    path("", views.station_list, name="station_list"),
    path("<int:station_id>/", views.station_detail, name="station_detail"),
    path(
        "<int:station_id>/manager/<int:agent_id>/",
        views.station_manager,
        name="station_manager",
    ),
    path("<int:station_id>/vehicles/", views.station_vehicles, name="station_vehicles"),
    path("<int:station_id>/occupancy/", views.station_occupancy_view, name="station_occupancy"),
]
