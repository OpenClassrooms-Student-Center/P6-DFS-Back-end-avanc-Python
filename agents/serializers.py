from rest_framework import serializers

from agents.models import Agent


class AgentSerializer(serializers.ModelSerializer):
    """Représentation JSON d'un agent."""

    class Meta:
        model = Agent
        fields = "__all__"
