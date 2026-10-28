"""Routage racine.

L'administration, les trois ressources de l'API, la documentation OpenAPI
et une redirection de la racine vers cette documentation.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.renderers import OpenApiJsonRenderer2
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Pas de page d'accueil : la racine redirige vers la documentation de l'API (Swagger UI).
    path("", RedirectView.as_view(pattern_name="docs"), name="root"),
    path("admin/", admin.site.urls),
    path("api/agents/", include("agents.urls")),
    path("api/stations/", include("stations.urls")),
    path("api/vehicles/", include("vehicles.urls")),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(renderer_classes=[OpenApiJsonRenderer2]),
        name="schema",
    ),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
