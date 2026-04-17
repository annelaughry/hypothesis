from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("select/", views.team_selection, name="team_selection"),  # View for team selection
    path("join/<int:team_id>/", views.join_team, name="join_team"),  # View to join a team
    path("force-join/", views.force_join_team, name="force_join_team"),  # View for forced selection
    path("", views.team_overview, name = "team_overview"),
    path("<int:team_id>/", views.team_detail, name="team_detail"),
]
