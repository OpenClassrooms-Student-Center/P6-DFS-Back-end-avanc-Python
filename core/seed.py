"""Jeu de données de démarrage.

Inséré par la commande `python manage.py seed` lorsque la base est vide,
afin que l'application soit utilisable dès le premier lancement.
"""

from django.db import transaction

from agents.models import Agent
from stations.models import Station
from vehicles.models import Vehicle


def seed_if_empty() -> bool:
    """Insère les agents, stations et véhicules de démarrage si la table des agents est vide.

    Retourne True si des données ont été insérées, False si la base était déjà peuplée.
    """
    if Agent.objects.exists():
        return False

    with transaction.atomic():
        tverdier = Agent.objects.create(
            username="tverdier",
            password="lead2024",
            full_name="Thomas Verdier",
            email="thomas.verdier@norlys-mobilite.fr",
            phone="06 12 34 56 78",
            role=Agent.Role.SUPERVISOR,
            is_active=True,
        )
        mlefranc = Agent.objects.create(
            username="mlefranc",
            password="stationA",
            full_name="Marion Lefranc",
            email="marion.lefranc@norlys-mobilite.fr",
            phone="06 23 45 67 89",
            role=Agent.Role.SUPERVISOR,
            is_active=True,
        )
        Agent.objects.create(
            username="kdiallo",
            password="velo123",
            full_name="Karim Diallo",
            email="karim.diallo@norlys-mobilite.fr",
            phone="06 34 56 78 90",
            role=Agent.Role.FIELD,
            is_active=True,
        )
        Agent.objects.create(
            username="sbernard",
            password="trott2023",
            full_name="Sophie Bernard",
            email="sophie.bernard@norlys-mobilite.fr",
            phone="06 45 67 89 01",
            role=Agent.Role.FIELD,
            is_active=False,
        )

        central_station = Station.objects.create(
            name="Gare Centrale",
            address="1 place de la Gare",
            capacity=20,
            latitude=48.8412,
            longitude=2.3218,
            is_active=True,
            manager=tverdier,
        )
        market_square = Station.objects.create(
            name="Place du Marché",
            address="14 rue des Halles",
            capacity=12,
            latitude=48.8455,
            longitude=2.3301,
            is_active=True,
            manager=mlefranc,
        )
        north_campus = Station.objects.create(
            name="Campus Nord",
            address="Avenue de l'Université",
            capacity=6,
            latitude=48.8620,
            longitude=2.3410,
            is_active=True,
            manager=None,
        )

        Vehicle.objects.bulk_create(
            [
                Vehicle(
                    serial_number="NRL-B-001",
                    type=Vehicle.Type.BIKE,
                    battery_level=92,
                    status=Vehicle.Status.AVAILABLE,
                    station=central_station,
                ),
                Vehicle(
                    serial_number="NRL-B-002",
                    type=Vehicle.Type.BIKE,
                    battery_level=15,
                    status=Vehicle.Status.LOW_BATTERY,
                    station=central_station,
                ),
                Vehicle(
                    serial_number="NRL-B-003",
                    type=Vehicle.Type.BIKE,
                    battery_level=60,
                    status=Vehicle.Status.MAINTENANCE,
                    station=central_station,
                ),
                Vehicle(
                    serial_number="NRL-S-001",
                    type=Vehicle.Type.SCOOTER,
                    battery_level=80,
                    status=Vehicle.Status.AVAILABLE,
                    station=market_square,
                ),
                Vehicle(
                    serial_number="NRL-S-002",
                    type=Vehicle.Type.SCOOTER,
                    battery_level=45,
                    status=Vehicle.Status.IN_USE,
                    station=None,
                ),
                Vehicle(
                    serial_number="NRL-S-003",
                    type=Vehicle.Type.SCOOTER,
                    battery_level=100,
                    status=Vehicle.Status.AVAILABLE,
                    station=north_campus,
                ),
                Vehicle(
                    serial_number="NRL-S-004",
                    type=Vehicle.Type.SCOOTER,
                    battery_level=33,
                    status=Vehicle.Status.AVAILABLE,
                    station=north_campus,
                ),
                Vehicle(
                    serial_number="NRL-B-004",
                    type=Vehicle.Type.BIKE,
                    battery_level=0,
                    status=Vehicle.Status.OUT_OF_SERVICE,
                    station=None,
                ),
            ]
        )

    return True
