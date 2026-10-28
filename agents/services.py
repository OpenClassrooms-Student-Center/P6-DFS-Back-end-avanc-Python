"""Règles de gestion des comptes d'agents : création, mot de passe, désactivation."""

from agents.models import Agent
from agents.selectors import email_exists, get_agent, username_exists
from core.exceptions import BusinessRuleError, ConflictError
from stations.selectors import is_station_manager


def _is_blank(value: str) -> bool:
    """Vrai si la chaîne ne contient que des espaces, ou rien."""
    return len(str(value).strip()) == 0


def create_agent(
    *,
    username: str | None,
    password: str | None,
    full_name: str = "",
    email: str | None = None,
    phone: str = "",
    role: str | None = None,
) -> Agent:
    """Crée un compte d'agent actif.

    L'identifiant est obligatoire et unique ; le mot de passe est obligatoire ;
    l'adresse e-mail, si elle est fournie, est unique elle aussi. Sans rôle
    explicite, l'agent est FIELD.
    """
    if username is None or _is_blank(value=username):
        raise BusinessRuleError("L'identifiant est obligatoire")
    username = str(username).strip()

    if password is None or _is_blank(value=password):
        raise BusinessRuleError("Le mot de passe est obligatoire")

    if username_exists(username=username):
        raise ConflictError(f"Identifiant déjà utilisé : {username}")

    # Une adresse vide équivaut à une absence d'adresse.
    if email is not None and _is_blank(value=email):
        email = None
    if email is not None and email_exists(email=email):
        raise ConflictError(f"Adresse e-mail déjà utilisée : {email}")

    return Agent.objects.create(
        username=username,
        password=password,
        full_name=full_name,
        email=email,
        phone=phone,
        role=role if role is not None else Agent.Role.FIELD,
        is_active=True,
    )


def change_password(agent_id: int, new_password: str | None) -> Agent:
    """Remplace le mot de passe d'un agent."""
    if new_password is None or _is_blank(value=new_password):
        raise BusinessRuleError("Le mot de passe est obligatoire")
    agent = get_agent(agent_id=agent_id)
    agent.password = new_password
    agent.save()
    return agent


def deactivate_agent(agent_id: int) -> None:
    """Désactive un agent sans supprimer son compte.

    Un agent responsable d'une station ne peut pas être désactivé : il faut
    d'abord désigner un autre responsable.
    """
    agent = get_agent(agent_id=agent_id)
    if is_station_manager(agent_id=agent_id):
        raise BusinessRuleError("Un agent responsable d'une station ne peut pas être désactivé")
    agent.is_active = False
    agent.save()
