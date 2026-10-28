from django.db import models


class Station(models.Model):
    """Station d'accueil des véhicules, avec une capacité et un éventuel responsable."""

    name = models.CharField(max_length=80)
    address = models.CharField(max_length=255, blank=True, default="")
    capacity = models.IntegerField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    manager = models.ForeignKey(
        to="agents.Agent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        db_table = "stations"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name="station_capacity_positive",
                violation_error_message="La capacité d'une station doit être strictement positive.",
            ),
        ]

    def has_free_slot(self, vehicle_count: int) -> bool:
        """Indique s'il reste au moins une place, étant donné le nombre de véhicules présents."""
        return vehicle_count < self.capacity

    def __str__(self) -> str:
        return self.name
