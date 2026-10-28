"""Point d'entrée WSGI du projet Norlys Mobilité."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "norlys_mobilite.settings")

application = get_wsgi_application()
