from django.contrib.auth import get_user_model
from .models import Team

def get_max_team_capacity():
    """Calculate equal team size based on total users"""
    total_users = get_user_model().objects.count()
    num_teams = Team.objects.count() or 1  # Prevent division by zero
    return total_users // num_teams

