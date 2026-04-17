from django.db.models.signals import post_save
from django.dispatch import receiver
from points.models import IndividualPoints
from .models import Team

@receiver(post_save, sender=IndividualPoints)
def update_team_leaderboard(sender, instance, **kwargs):
    """Automatically update team leader when points change"""
    if instance.user.team.exists():
        team = instance.user.team.first()
        team.update_leaderboard()


