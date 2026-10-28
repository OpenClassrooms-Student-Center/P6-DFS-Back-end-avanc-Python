from django.db import models

# Niveau de batterie minimal pour qu'un véhicule soit louable.
MIN_BATTERY_FOR_RENTAL = 20

# Niveau de batterie maximal.
MAX_BATTERY_LEVEL = 100


class Vehicle(models.Model):
    """Véhicule de la flotte (vélo ou trottinette) et son cycle de vie.

    AVAILABLE      : en état de rouler ; louable une fois en station.
    IN_USE         : en cours de location, hors station.
    LOW_BATTERY    : batterie sous le seuil de location.
    MAINTENANCE    : immobilisé pour intervention technique.
    OUT_OF_SERVICE : retiré définitivement de la flotte.
    """

    class Type(models.TextChoices):
        BIKE = "BIKE", "Vélo"
        SCOOTER = "SCOOTER", "Trottinette"

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Disponible"
        IN_USE = "IN_USE", "En cours d'utilisation"
        LOW_BATTERY = "LOW_BATTERY", "Batterie faible"
        MAINTENANCE = "MAINTENANCE", "En maintenance"
        OUT_OF_SERVICE = "OUT_OF_SERVICE", "Retiré"

    serial_number = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=10, choices=Type.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    battery_level = models.IntegerField(default=100)
    station = models.ForeignKey(
        to="stations.Station",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    last_maintenance_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "vehicles"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(battery_level__gte=0, battery_level__lte=MAX_BATTERY_LEVEL),
                name="vehicle_battery_level_range",
                violation_error_message="Le niveau de batterie doit être compris entre 0 et 100.",
            ),
        ]

    @staticmethod
    def status_for_battery(level: int) -> str:
        """Statut d'un véhicule en état de rouler selon son niveau de batterie."""
        if level < MIN_BATTERY_FOR_RENTAL:
            return Vehicle.Status.LOW_BATTERY
        return Vehicle.Status.AVAILABLE

    def __str__(self) -> str:
        return self.serial_number
