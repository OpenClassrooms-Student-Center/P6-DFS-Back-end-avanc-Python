from django.urls import path

from agents import views

app_name = "agents"

urlpatterns = [
    path("", views.agent_list, name="agent_list"),
    path("<int:agent_id>/", views.agent_detail, name="agent_detail"),
    path("<int:agent_id>/password/", views.agent_password, name="agent_password"),
]
