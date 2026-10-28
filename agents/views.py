"""Points d'entrée HTTP de la ressource agents (/api/agents/).

Les décorateurs `@extend_schema` documentent l'API dans Swagger ; ils ne valident rien.
"""

from http import HTTPMethod

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from agents.models import Agent
from agents.selectors import get_agent, list_agents
from agents.serializers import AgentSerializer
from agents.services import change_password, create_agent, deactivate_agent

# Corps attendu en création (documentation uniquement).
_AGENT_CREATE_REQUEST = inline_serializer(
    name="AgentCreateRequest",
    fields={
        "username": serializers.CharField(),
        "password": serializers.CharField(),
        "full_name": serializers.CharField(required=False),
        "email": serializers.EmailField(required=False),
        "phone": serializers.CharField(required=False),
        "role": serializers.ChoiceField(choices=Agent.Role.choices, required=False),
    },
)

# Corps attendu en changement de mot de passe (documentation uniquement).
_AGENT_PASSWORD_REQUEST = inline_serializer(
    name="AgentPasswordRequest",
    fields={"password": serializers.CharField()},
)


@extend_schema(
    methods=[HTTPMethod.GET], summary="Liste des agents", responses=AgentSerializer(many=True)
)
@extend_schema(
    methods=[HTTPMethod.POST],
    summary="Création d'un agent",
    request=_AGENT_CREATE_REQUEST,
    responses={201: AgentSerializer},
)
@api_view([HTTPMethod.GET, HTTPMethod.POST])
def agent_list(request: Request) -> Response:
    """Liste des agents, ou création d'un agent."""
    match request.method:
        case HTTPMethod.POST:
            data = request.data
            agent = create_agent(
                username=data.get("username"),
                password=data.get("password"),
                full_name=data.get("full_name", ""),
                email=data.get("email"),
                phone=data.get("phone", ""),
                role=data.get("role"),
            )
            return Response(AgentSerializer(agent).data, status=status.HTTP_201_CREATED)
        case _:
            return Response(AgentSerializer(list_agents(), many=True).data)


@extend_schema(methods=[HTTPMethod.GET], summary="Détail d'un agent", responses=AgentSerializer)
@extend_schema(
    methods=[HTTPMethod.DELETE], summary="Désactivation d'un agent", responses={204: None}
)
@api_view([HTTPMethod.GET, HTTPMethod.DELETE])
def agent_detail(request: Request, agent_id: int) -> Response:
    """Détail d'un agent, ou désactivation de son compte."""
    match request.method:
        case HTTPMethod.DELETE:
            deactivate_agent(agent_id=agent_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        case _:
            return Response(AgentSerializer(get_agent(agent_id=agent_id)).data)


@extend_schema(
    summary="Changement du mot de passe d'un agent",
    request=_AGENT_PASSWORD_REQUEST,
    responses=AgentSerializer,
)
@api_view([HTTPMethod.PUT])
def agent_password(request: Request, agent_id: int) -> Response:
    """Changement du mot de passe d'un agent. Corps attendu : {"password": "..."}."""
    agent = change_password(agent_id=agent_id, new_password=request.data.get("password"))
    return Response(AgentSerializer(agent).data)
