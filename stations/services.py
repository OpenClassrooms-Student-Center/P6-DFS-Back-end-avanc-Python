"""Règles de gestion des stations : capacité, responsable, désactivation, occupation."""

from dataclasses import dataclass

from django.db.models import QuerySet

from agents.models import Agent
from agents.selectors import get_agent
from core.exceptions import BusinessRuleError
from stations.models import Station
from stations.selectors import get_station
from vehicles.models import Vehicle
from vehicles.selectors import count_vehicles_in_station, list_vehicles_in_station


@dataclass(frozen=True)
class StationOccupancy:
    """Vue calculée de l'occupation d'une station à un instant donné."""

    station_id: int
    capacity: int
    vehicle_count: int
    available_slots: int
    occupancy_rate: float


def compute_occupancy(station_id: int, capacity: int, vehicle_count: int) -> StationOccupancy:
    """Calcule l'occupation d'une station.

    Les places restantes ne sont jamais négatives ; le taux d'occupation
    est arrondi à 2 décimales.
    """
    available_slots = max(0, capacity - vehicle_count)
    occupancy_rate = round(vehicle_count / capacity, 2)
    return StationOccupancy(
        station_id=station_id,
        capacity=capacity,
        vehicle_count=vehicle_count,
        available_slots=available_slots,
        occupancy_rate=occupancy_rate,
    )


def _require_positive_capacity(capacity: int) -> None:
    if capacity <= 0:
        raise BusinessRuleError("La capacité d'une station doit être strictement positive")


def create_station(
    *,
    name: str,
    address: str = "",
    capacity: int,
    latitude: float | None = None,
    longitude: float | None = None,
) -> Station:
    """Crée une station active de capacité strictement positive."""
    _require_positive_capacity(capacity=capacity)
    return Station.objects.create(
        name=name,
        address=address,
        capacity=capacity,
        latitude=latitude,
        longitude=longitude,
        is_active=True,
    )


def update_station(
    station_id: int,
    *,
    name: str,
    address: str,
    capacity: int,
    latitude: float | None,
    longitude: float | None,
) -> Station:
    """Met à jour nom, adresse, capacité et coordonnées d'une station.

    La capacité reste strictement positive et ne peut pas descendre sous le
    nombre de véhicules actuellement présents.
    """
    station = get_station(station_id=station_id)
    _require_positive_capacity(capacity=capacity)

    vehicles_present = count_vehicles_in_station(station_id=station_id)
    if capacity < vehicles_present:
        raise BusinessRuleError(
            "La capacité ne peut pas être inférieure au nombre de véhicules présents"
        )

    station.name = name
    station.address = address
    station.capacity = capacity
    station.latitude = latitude
    station.longitude = longitude
    station.save()
    return station


def assign_manager(station_id: int, agent_id: int) -> Station:
    """Désigne le responsable d'une station : un agent actif ayant le rôle SUPERVISOR."""
    station = get_station(station_id=station_id)
    agent = get_agent(agent_id=agent_id)

    if not agent.is_active:
        raise BusinessRuleError("Un agent désactivé ne peut pas gérer une station")
    if agent.role != Agent.Role.SUPERVISOR:
        raise BusinessRuleError("Seul un superviseur peut gérer une station")

    station.manager = agent
    station.save()
    return station


def deactivate_station(station_id: int) -> None:
    """Désactive une station, à condition qu'elle ne contienne aucun véhicule."""
    station = get_station(station_id=station_id)
    if count_vehicles_in_station(station_id=station_id) > 0:
        raise BusinessRuleError("Une station occupée ne peut pas être désactivée")
    station.is_active = False
    station.save()


def vehicles_of(station_id: int) -> QuerySet[Vehicle]:
    """Véhicules présents dans une station existante."""
    get_station(station_id=station_id)
    return list_vehicles_in_station(station_id=station_id)


def station_occupancy(station_id: int) -> StationOccupancy:
    """Occupation courante d'une station existante."""
    station = get_station(station_id=station_id)
    return compute_occupancy(
        station_id=station.id,
        capacity=station.capacity,
        vehicle_count=count_vehicles_in_station(station_id=station_id),
    )
