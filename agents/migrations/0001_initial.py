from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Agent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("username", models.CharField(max_length=50, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("full_name", models.CharField(blank=True, default="", max_length=100)),
                ("email", models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ("phone", models.CharField(blank=True, default="", max_length=20)),
                (
                    "role",
                    models.CharField(
                        choices=[("FIELD", "Agent de terrain"), ("SUPERVISOR", "Superviseur")],
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "agents",
                "ordering": ["id"],
            },
        ),
    ]
