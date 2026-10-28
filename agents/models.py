from django.db import models


class Agent(models.Model):
    """Compte d'un agent de l'organisation.

    Un agent FIELD intervient sur les stations et les véhicules ;
    un SUPERVISOR encadre une ou plusieurs stations.
    """

    class Role(models.TextChoices):
        FIELD = "FIELD", "Agent de terrain"
        SUPERVISOR = "SUPERVISOR", "Superviseur"

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    full_name = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    role = models.CharField(max_length=20, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "agents"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.username
