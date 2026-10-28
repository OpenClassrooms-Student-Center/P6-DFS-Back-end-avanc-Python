"""Point d'entrée ASGI du projet Norlys Mobilité."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "norlys_mobilite.settings")

application = get_asgi_application()
