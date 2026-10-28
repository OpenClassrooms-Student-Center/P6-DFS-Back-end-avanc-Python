"""Commande `python manage.py seed` : insère le jeu de données de démarrage."""

from django.core.management.base import BaseCommand

from core.seed import seed_if_empty


class Command(BaseCommand):
    help = "Insère les agents, stations et véhicules de démarrage si la base est vide."

    def handle(self, *args: object, **options: object) -> None:
        inserted = seed_if_empty()
        if inserted:
            self.stdout.write(self.style.SUCCESS("Données de démarrage insérées."))
        else:
            self.stdout.write("Base déjà initialisée, aucune donnée insérée.")
