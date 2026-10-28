"""Points d'entrée HTTP de la ressource stations (/api/stations/).

Les décorateurs `@extend_schema` documentent l'API dans Swagger ; ils ne valident rien.
"""

from dataclasses import asdict
from http import HTTPMethod

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from stations.selectors import get_station, list_stations
from stations.serializers import StationOccupancySerializer, StationSerializer
from stations.services import (
    assign_manager,
    create_station,
    deactivate_station,
    station_occupancy,
    update_station,
    vehicles_of,
)
from vehicles.serializers import VehicleSerializer

# Corps attendu en création et en mise à jour (documentation uniquement).
_STATION_WRITE_REQUEST = inline_serializer(
    name="StationWriteRequest",
    fields={
        "name": serializers.CharField(),
        "address": serializers.CharField(required=False),
        "capacity": serializers.IntegerField(),
        "latitude": serializers.FloatField(required=False, allow_null=True),
        "longitude": serializers.FloatField(required=False, allow_null=True),
    },
)


@extend_schema(
    methods=[HTTPMethod.GET], summary="Liste des stations", responses=StationSerializer(many=True)
)
@extend_schema(
    methods=[HTTPMethod.POST],
    summary="Création d'une station",
    request=_STATION_WRITE_REQUEST,
    responses={201: StationSerializer},
)
@api_view([HTTPMethod.GET, HTTPMethod.POST])
def station_list(request: Request) -> Response:
    """Liste des stations, ou création d'une station."""
    match request.method:
        case HTTPMethod.POST:
            data = request.data
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            station = create_station(
                name=data.get("name"),
                address=data.get("address", ""),
                capacity=int(data.get("capacity", 0)),
                latitude=float(latitude) if latitude is not None else None,
                longitude=float(longitude) if longitude is not None else None,
            )
            return Response(StationSerializer(station).data, status=status.HTTP_201_CREATED)
        case _:
            return Response(StationSerializer(list_stations(), many=True).data)


@extend_schema(
    methods=[HTTPMethod.GET], summary="Détail d'une station", responses=StationSerializer
)
@extend_schema(
    methods=[HTTPMethod.PUT],
    summary="Mise à jour d'une station",
    request=_STATION_WRITE_REQUEST,
    responses=StationSerializer,
)
@extend_schema(
    methods=[HTTPMethod.DELETE], summary="Désactivation d'une station", responses={204: None}
)
@api_view([HTTPMethod.GET, HTTPMethod.PUT, HTTPMethod.DELETE])
def station_detail(request: Request, station_id: int) -> Response:
    """Détail, mise à jour ou désactivation d'une station."""
    match request.method:
        case HTTPMethod.PUT:
            data = request.data
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            station = update_station(
                station_id=station_id,
                name=data.get("name"),
                address=data.get("address", ""),
                capacity=int(data.get("capacity", 0)),
                latitude=float(latitude) if latitude is not None else None,
                longitude=float(longitude) if longitude is not None else None,
            )
            return Response(StationSerializer(station).data)
        case HTTPMethod.DELETE:
            deactivate_station(station_id=station_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        case _:
            return Response(StationSerializer(get_station(station_id=station_id)).data)


@extend_schema(
    summary="Désignation du responsable d'une station", request=None, responses=StationSerializer
)
@api_view([HTTPMethod.PUT])
def station_manager(request: Request, station_id: int, agent_id: int) -> Response:
    """Désignation du responsable d'une station."""
    station = assign_manager(station_id=station_id, agent_id=agent_id)
    return Response(StationSerializer(station).data)


@extend_schema(
    summary="Véhicules présents dans une station", responses=VehicleSerializer(many=True)
)
@api_view([HTTPMethod.GET])
def station_vehicles(request: Request, station_id: int) -> Response:
    """Véhicules présents dans une station."""
    return Response(VehicleSerializer(vehicles_of(station_id=station_id), many=True).data)


@extend_schema(summary="Occupation d'une station", responses=StationOccupancySerializer)
@api_view([HTTPMethod.GET])
def station_occupancy_view(request: Request, station_id: int) -> Response:
    """Occupation d'une station : places libres et taux."""
    occupancy = station_occupancy(station_id=station_id)
    return Response(StationOccupancySerializer(asdict(occupancy)).data)
