from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Team
from .utils import get_max_team_capacity
from django.shortcuts import render, get_object_or_404

def team_selection(request):
    """View for users to select a team"""
    teams = Team.objects.all()
    return render(request, "team_selection.html", {"teams": teams})


def join_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # ✅ Prevent multiple "already in team" messages
    if request.user.team:
        if not any("already in a team" in msg.message for msg in messages.get_messages(request)):
            messages.error(request, "You are already in a team!")
        return redirect("teams:team_overview")
    
    if request.user.has_team_join_expired():
        messages.error(request, "Your team selection deadline has passed. Contact an admin.")
        return redirect("users:profile")

    # ✅ Ensure team is not full
    if team.members.count() >= team.max_members:
        messages.error(request, "This team is full. Please choose another team.")
        return redirect("teams:team_selection")

    # ✅ Assign user to team
    request.user.team = team
    request.user.save(update_fields=['team'])
    team.members.add(request.user)

    # ✅ Clear previous messages before adding a new one
    messages.get_messages(request).used = True
    messages.success(request, f"You have joined {team.name}!")

    return redirect("teams:team_overview")


def force_join_team(request):
    """Force users to pick a team after 30 days"""
    if request.user.profile.team_joined:
        return redirect("dashboard")

    teams = Team.objects.all()
    return render(request, "force_join_team.html", {"teams": teams})

def team_overview(request):
    """Displays all teams with their leaderboard and stats."""
    teams = list(Team.objects.all())  # ✅ Convert QuerySet to list
    teams.sort(key=lambda team: team.total_points, reverse=True)  # ✅ Sort by total points

    # Add leaderboard student for each team
    for team in teams:
        team.leaderboard_student = max(
            team.members.all(), 
            key=lambda user: user.profile.points if hasattr(user, "profile") else 0,
            default=None
        )

    return render(request, "team_overview.html", {"teams": teams})

def team_detail(request, team_id):
    """Displays detailed information about a specific team."""
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()
    return render(request, "team_detail.html", {"team": team, "members": members})