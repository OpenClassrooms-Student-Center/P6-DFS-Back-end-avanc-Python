"""Lectures et recherches sur les stations."""

from django.db.models import QuerySet

from core.exceptions import ResourceNotFoundError
from stations.models import Station


def list_stations() -> QuerySet[Station]:
    """Toutes les stations, actives ou non, par identifiant croissant."""
    return Station.objects.all()


def get_station(station_id: int) -> Station:
    """Retourne la station d'identifiant donné, ou lève ResourceNotFoundError."""
    try:
        return Station.objects.get(pk=station_id)
    except Station.DoesNotExist as exc:
        raise ResourceNotFoundError(f"Station introuvable : {station_id}") from exc


def is_station_manager(agent_id: int) -> bool:
    """Indique si l'agent est responsable d'au moins une station."""
    return Station.objects.filter(manager_id=agent_id).exists()
