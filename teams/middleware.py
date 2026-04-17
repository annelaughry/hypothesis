from django.shortcuts import redirect
from datetime import date

class TeamJoinMiddleware:
    """Middleware to force users to join a team within 30 days"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            profile = request.user.profile
            if not profile.team_joined:
                if profile.join_deadline and date.today() > profile.join_deadline:
                    return redirect("force_join_team")  # Redirect users after 30 days
                else:
                    request.session["team_join_reminder"] = "You need to join a team within 30 days!"
        return self.get_response(request)
