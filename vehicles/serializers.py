from rest_framework import serializers

from stations.serializers import StationSerializer
from vehicles.models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """Représentation JSON d'un véhicule, station de rattachement incluse."""

    station = StationSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = "__all__"
