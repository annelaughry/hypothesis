from django.db.models import Sum
from points.models import Points
from django.conf import settings

def user_level_and_team(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    # Points → level color
    total_points = Points.objects.filter(user=user).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

    if total_points >= 600:
        level_color = "#ffd700"
    elif total_points >= 400:
        level_color = "#1e90ff"
    elif total_points >= 100:
        level_color = "#32cd32"
    else:
        level_color = "#d3d3d3"

    # Determine avatar or fallback
    profile_pic = "/static/images/logo.png"  # default fallback

    if hasattr(user, 'profile'):
        profile = user.profile
        try:
            if profile.avatar:
                profile_pic = profile.avatar.url
            elif profile.generated_avatar:
                profile_pic = profile.generated_avatar.url
        except Exception:
            pass

    return {
        'nav_level_color': level_color,
        'nav_profile_pic': profile_pic,
    }
