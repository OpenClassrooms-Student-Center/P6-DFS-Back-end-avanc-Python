import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("agents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Station",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=80)),
                ("address", models.CharField(blank=True, default="", max_length=255)),
                ("capacity", models.IntegerField()),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "manager",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="agents.agent",
                    ),
                ),
            ],
            options={
                "db_table": "stations",
                "ordering": ["id"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("capacity__gt", 0)),
                        name="station_capacity_positive",
                        violation_error_message=(
                            "La capacité d'une station doit être strictement positive."
                        ),
                    )
                ],
            },
        ),
    ]
