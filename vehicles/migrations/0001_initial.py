import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("stations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("serial_number", models.CharField(max_length=30, unique=True)),
                (
                    "type",
                    models.CharField(
                        choices=[("BIKE", "Vélo"), ("SCOOTER", "Trottinette")], max_length=10
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AVAILABLE", "Disponible"),
                            ("IN_USE", "En cours d'utilisation"),
                            ("LOW_BATTERY", "Batterie faible"),
                            ("MAINTENANCE", "En maintenance"),
                            ("OUT_OF_SERVICE", "Retiré"),
                        ],
                        default="AVAILABLE",
                        max_length=20,
                    ),
                ),
                ("battery_level", models.IntegerField(default=100)),
                ("last_maintenance_at", models.DateTimeField(blank=True, null=True)),
                (
                    "station",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="stations.station",
                    ),
                ),
            ],
            options={
                "db_table": "vehicles",
                "ordering": ["id"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("battery_level__gte", 0), ("battery_level__lte", 100)),
                        name="vehicle_battery_level_range",
                        violation_error_message=(
                            "Le niveau de batterie doit être compris entre 0 et 100."
                        ),
                    )
                ],
            },
        ),
    ]
