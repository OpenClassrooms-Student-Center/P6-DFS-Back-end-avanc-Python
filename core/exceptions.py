"""Exceptions métier partagées par les applications du projet."""


class ResourceNotFoundError(Exception):
    """Levée lorsqu'une ressource demandée (station, véhicule, agent) n'existe pas."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BusinessRuleError(Exception):
    """Levée lorsqu'une opération viole une règle de gestion
    (station pleine, véhicule non disponible, capacité invalide...).
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConflictError(BusinessRuleError):
    """Levée lorsqu'une création entre en conflit avec une ressource existante
    (identifiant, adresse e-mail ou numéro de série déjà utilisé).
    """
