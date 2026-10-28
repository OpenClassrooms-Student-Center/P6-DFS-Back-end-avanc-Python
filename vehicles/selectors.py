"""Lectures et recherches sur les véhicules de la flotte."""

from django.db.models import QuerySet

from core.exceptions import ResourceNotFoundError
from vehicles.models import Vehicle


def list_vehicles() -> QuerySet[Vehicle]:
    """Tous les véhicules de la flotte, par identifiant croissant."""
    return Vehicle.objects.all()


def get_vehicle(vehicle_id: int) -> Vehicle:
    """Retourne le véhicule d'identifiant donné, ou lève ResourceNotFoundError."""
    try:
        return Vehicle.objects.get(pk=vehicle_id)
    except Vehicle.DoesNotExist as exc:
        raise ResourceNotFoundError(f"Véhicule introuvable : {vehicle_id}") from exc


def list_vehicles_in_station(station_id: int) -> QuerySet[Vehicle]:
    """Véhicules actuellement rattachés à la station donnée."""
    return Vehicle.objects.filter(station_id=station_id)


def count_vehicles_in_station(station_id: int) -> int:
    """Nombre de véhicules actuellement rattachés à la station donnée."""
    return Vehicle.objects.filter(station_id=station_id).count()


def serial_number_exists(serial_number: str) -> bool:
    """Indique si un véhicule porte déjà ce numéro de série."""
    return Vehicle.objects.filter(serial_number=serial_number).exists()
