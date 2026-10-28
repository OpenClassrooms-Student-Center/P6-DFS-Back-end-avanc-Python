from rest_framework import serializers

from agents.serializers import AgentSerializer
from stations.models import Station


class StationSerializer(serializers.ModelSerializer):
    """Représentation JSON d'une station, responsable inclus."""

    manager = AgentSerializer(read_only=True)

    class Meta:
        model = Station
        fields = "__all__"


class StationOccupancySerializer(serializers.Serializer):
    """Représentation JSON de l'occupation d'une station."""

    station_id = serializers.IntegerField()
    capacity = serializers.IntegerField()
    vehicle_count = serializers.IntegerField()
    available_slots = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
