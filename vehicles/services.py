"""Règles de gestion de la flotte.

Affectation en station, location, batterie, maintenance, retrait.
"""

from django.utils import timezone

from core.exceptions import BusinessRuleError, ConflictError
from stations.models import Station
from stations.selectors import get_station
from vehicles.models import MAX_BATTERY_LEVEL, MIN_BATTERY_FOR_RENTAL, Vehicle
from vehicles.selectors import count_vehicles_in_station, get_vehicle, serial_number_exists


def _require_valid_battery(level: int) -> None:
    if level < 0 or level > MAX_BATTERY_LEVEL:
        raise BusinessRuleError("Le niveau de batterie doit être compris entre 0 et 100")


def _require_active_station(station: Station) -> None:
    if not station.is_active:
        raise BusinessRuleError("La station est désactivée")


def _require_free_slot(station: Station) -> None:
    if not station.has_free_slot(vehicle_count=count_vehicles_in_station(station_id=station.id)):
        raise BusinessRuleError("La station est pleine")


def create_vehicle(*, serial_number: str, vehicle_type: str, battery_level: int = 100) -> Vehicle:
    """Ajoute un véhicule à la flotte, hors station, avec un statut déduit de sa batterie."""
    if serial_number_exists(serial_number=serial_number):
        raise ConflictError(f"Numéro de série déjà utilisé : {serial_number}")
    _require_valid_battery(level=battery_level)

    return Vehicle.objects.create(
        serial_number=serial_number,
        type=vehicle_type,
        battery_level=battery_level,
        status=Vehicle.status_for_battery(level=battery_level),
        station=None,
    )


def assign_to_station(vehicle_id: int, station_id: int) -> Vehicle:
    """Rattache un véhicule à une station active et non pleine."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)
    station = get_station(station_id=station_id)

    _require_active_station(station=station)
    if vehicle.status == Vehicle.Status.IN_USE:
        raise BusinessRuleError("Un véhicule en cours d'utilisation ne peut pas être affecté")
    if vehicle.status == Vehicle.Status.OUT_OF_SERVICE:
        raise BusinessRuleError("Un véhicule retiré ne peut pas être affecté")
    # Le véhicule est déjà dans cette station : rien à faire.
    if vehicle.station_id == station.id:
        return vehicle
    _require_free_slot(station=station)

    vehicle.station = station
    vehicle.save()
    return vehicle


def start_rental(vehicle_id: int) -> Vehicle:
    """Démarre une location : le véhicule quitte sa station et passe IN_USE."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)

    if vehicle.status != Vehicle.Status.AVAILABLE:
        raise BusinessRuleError("Le véhicule n'est pas disponible")
    if vehicle.station_id is None:
        raise BusinessRuleError("Le véhicule n'est rattaché à aucune station")
    if vehicle.battery_level < MIN_BATTERY_FOR_RENTAL:
        raise BusinessRuleError("Batterie insuffisante pour une location")

    vehicle.status = Vehicle.Status.IN_USE
    vehicle.station = None
    vehicle.save()
    return vehicle


def end_rental(vehicle_id: int, station_id: int, battery_level: int) -> Vehicle:
    """Termine une location : le véhicule rejoint une station et son statut est recalculé."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)

    if vehicle.status != Vehicle.Status.IN_USE:
        raise BusinessRuleError("Le véhicule n'est pas en cours d'utilisation")
    _require_valid_battery(level=battery_level)

    station = get_station(station_id=station_id)
    _require_active_station(station=station)
    _require_free_slot(station=station)

    vehicle.station = station
    vehicle.battery_level = battery_level
    vehicle.status = Vehicle.status_for_battery(level=battery_level)
    vehicle.save()
    return vehicle


def update_battery(vehicle_id: int, level: int) -> Vehicle:
    """Met à jour le niveau de batterie et fait basculer AVAILABLE / LOW_BATTERY autour du seuil."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)
    _require_valid_battery(level=level)

    vehicle.battery_level = level
    if vehicle.status == Vehicle.Status.LOW_BATTERY and level >= MIN_BATTERY_FOR_RENTAL:
        vehicle.status = Vehicle.Status.AVAILABLE
    elif vehicle.status == Vehicle.Status.AVAILABLE and level < MIN_BATTERY_FOR_RENTAL:
        vehicle.status = Vehicle.Status.LOW_BATTERY
    vehicle.save()
    return vehicle


def send_to_maintenance(vehicle_id: int) -> Vehicle:
    """Immobilise un véhicule pour intervention technique."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)

    if vehicle.status == Vehicle.Status.IN_USE:
        raise BusinessRuleError(
            "Un véhicule en cours d'utilisation ne peut pas partir en maintenance"
        )
    if vehicle.status == Vehicle.Status.OUT_OF_SERVICE:
        raise BusinessRuleError("Un véhicule retiré ne peut pas partir en maintenance")

    vehicle.status = Vehicle.Status.MAINTENANCE
    vehicle.save()
    return vehicle


def return_from_maintenance(vehicle_id: int) -> Vehicle:
    """Remet en service un véhicule sorti de maintenance et date l'intervention."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)

    if vehicle.status != Vehicle.Status.MAINTENANCE:
        raise BusinessRuleError("Le véhicule n'est pas en maintenance")

    vehicle.last_maintenance_at = timezone.now()
    vehicle.status = Vehicle.status_for_battery(level=vehicle.battery_level)
    vehicle.save()
    return vehicle


def retire_vehicle(vehicle_id: int) -> None:
    """Retire définitivement un véhicule de la flotte."""
    vehicle = get_vehicle(vehicle_id=vehicle_id)

    if vehicle.status == Vehicle.Status.IN_USE:
        raise BusinessRuleError("Un véhicule en cours d'utilisation ne peut pas être retiré")

    vehicle.status = Vehicle.Status.OUT_OF_SERVICE
    vehicle.station = None
    vehicle.save()
