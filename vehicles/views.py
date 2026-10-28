"""Points d'entrée HTTP de la ressource véhicules (/api/vehicles/).

Les décorateurs `@extend_schema` documentent l'API dans Swagger ; ils ne valident rien.
"""

from http import HTTPMethod

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from vehicles.models import Vehicle
from vehicles.selectors import get_vehicle, list_vehicles
from vehicles.serializers import VehicleSerializer
from vehicles.services import (
    assign_to_station,
    create_vehicle,
    end_rental,
    retire_vehicle,
    return_from_maintenance,
    send_to_maintenance,
    start_rental,
    update_battery,
)

# Corps attendu en création (documentation uniquement).
_VEHICLE_CREATE_REQUEST = inline_serializer(
    name="VehicleCreateRequest",
    fields={
        "serial_number": serializers.CharField(),
        "type": serializers.ChoiceField(choices=Vehicle.Type.choices),
        "battery_level": serializers.IntegerField(required=False),
    },
)

# Corps attendu en fin de location (documentation uniquement).
_RENTAL_END_REQUEST = inline_serializer(
    name="RentalEndRequest",
    fields={
        "station_id": serializers.IntegerField(),
        "battery_level": serializers.IntegerField(),
    },
)

# Corps attendu en mise à jour de la batterie (documentation uniquement).
_BATTERY_REQUEST = inline_serializer(
    name="BatteryRequest",
    fields={"level": serializers.IntegerField()},
)


@extend_schema(
    methods=[HTTPMethod.GET], summary="Liste des véhicules", responses=VehicleSerializer(many=True)
)
@extend_schema(
    methods=[HTTPMethod.POST],
    summary="Ajout d'un véhicule à la flotte",
    request=_VEHICLE_CREATE_REQUEST,
    responses={201: VehicleSerializer},
)
@api_view([HTTPMethod.GET, HTTPMethod.POST])
def vehicle_list(request: Request) -> Response:
    """Liste des véhicules, ou ajout d'un véhicule à la flotte."""
    match request.method:
        case HTTPMethod.POST:
            data = request.data
            vehicle = create_vehicle(
                serial_number=data.get("serial_number"),
                vehicle_type=data.get("type"),
                battery_level=int(data.get("battery_level", 100)),
            )
            return Response(VehicleSerializer(vehicle).data, status=status.HTTP_201_CREATED)
        case _:
            return Response(VehicleSerializer(list_vehicles(), many=True).data)


@extend_schema(
    methods=[HTTPMethod.GET], summary="Détail d'un véhicule", responses=VehicleSerializer
)
@extend_schema(
    methods=[HTTPMethod.DELETE], summary="Retrait définitif de la flotte", responses={204: None}
)
@api_view([HTTPMethod.GET, HTTPMethod.DELETE])
def vehicle_detail(request: Request, vehicle_id: int) -> Response:
    """Détail d'un véhicule, ou retrait définitif de la flotte."""
    match request.method:
        case HTTPMethod.DELETE:
            retire_vehicle(vehicle_id=vehicle_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        case _:
            return Response(VehicleSerializer(get_vehicle(vehicle_id=vehicle_id)).data)


@extend_schema(
    summary="Affectation d'un véhicule à une station", request=None, responses=VehicleSerializer
)
@api_view([HTTPMethod.PUT])
def vehicle_station(request: Request, vehicle_id: int, station_id: int) -> Response:
    """Affectation d'un véhicule à une station."""
    vehicle = assign_to_station(vehicle_id=vehicle_id, station_id=station_id)
    return Response(VehicleSerializer(vehicle).data)


@extend_schema(summary="Début de location", request=None, responses=VehicleSerializer)
@api_view([HTTPMethod.POST])
def vehicle_rental_start(request: Request, vehicle_id: int) -> Response:
    """Début de location."""
    vehicle = start_rental(vehicle_id=vehicle_id)
    return Response(VehicleSerializer(vehicle).data)


@extend_schema(
    summary="Fin de location",
    request=_RENTAL_END_REQUEST,
    responses=VehicleSerializer,
)
@api_view([HTTPMethod.POST])
def vehicle_rental_end(request: Request, vehicle_id: int) -> Response:
    """Fin de location. Corps attendu : {"station_id": ..., "battery_level": ...}."""
    station_id = int(request.data.get("station_id"))
    battery_level = int(request.data.get("battery_level"))
    vehicle = end_rental(vehicle_id=vehicle_id, station_id=station_id, battery_level=battery_level)
    return Response(VehicleSerializer(vehicle).data)


@extend_schema(
    summary="Mise à jour du niveau de batterie",
    request=_BATTERY_REQUEST,
    responses=VehicleSerializer,
)
@api_view([HTTPMethod.PUT])
def vehicle_battery(request: Request, vehicle_id: int) -> Response:
    """Mise à jour du niveau de batterie. Corps attendu : {"level": ...}."""
    level = int(request.data.get("level"))
    vehicle = update_battery(vehicle_id=vehicle_id, level=level)
    return Response(VehicleSerializer(vehicle).data)


@extend_schema(summary="Envoi en maintenance", request=None, responses=VehicleSerializer)
@api_view([HTTPMethod.POST])
def vehicle_maintenance(request: Request, vehicle_id: int) -> Response:
    """Envoi en maintenance."""
    vehicle = send_to_maintenance(vehicle_id=vehicle_id)
    return Response(VehicleSerializer(vehicle).data)


@extend_schema(summary="Retour de maintenance", request=None, responses=VehicleSerializer)
@api_view([HTTPMethod.POST])
def vehicle_maintenance_return(request: Request, vehicle_id: int) -> Response:
    """Retour de maintenance."""
    vehicle = return_from_maintenance(vehicle_id=vehicle_id)
    return Response(VehicleSerializer(vehicle).data)
