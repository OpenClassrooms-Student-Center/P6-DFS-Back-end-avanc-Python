"""Lectures et recherches sur les agents.

Seul point d'accès en lecture à la table `agents` : les services et les vues
passent par ces fonctions plutôt que par l'ORM directement.
"""

from django.db.models import QuerySet

from agents.models import Agent
from core.exceptions import ResourceNotFoundError


def list_agents() -> QuerySet[Agent]:
    """Tous les agents, actifs ou non, par identifiant croissant."""
    return Agent.objects.all()


def get_agent(agent_id: int) -> Agent:
    """Retourne l'agent d'identifiant donné, ou lève ResourceNotFoundError."""
    try:
        return Agent.objects.get(pk=agent_id)
    except Agent.DoesNotExist as exc:
        raise ResourceNotFoundError(f"Agent introuvable : {agent_id}") from exc


def username_exists(username: str) -> bool:
    """Indique si un agent porte déjà cet identifiant de connexion."""
    return Agent.objects.filter(username=username).exists()


def email_exists(email: str) -> bool:
    """Indique si un agent utilise déjà cette adresse e-mail."""
    return Agent.objects.filter(email=email).exists()
