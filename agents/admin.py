from django.contrib import admin

from agents.models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("username", "full_name", "email", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "full_name", "email")
