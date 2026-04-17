from teams.models import Team

def team_logos(request):
    """Pass team logos to base.html for display in navbar."""
    teams = list(Team.objects.all())  # Convert QuerySet to list
    teams.sort(key=lambda team: team.total_points, reverse=True)  # Sort manually  # ✅ Order by team ranking
    return {'teams': teams}
