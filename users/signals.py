from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser, Profile
import logging
from django.contrib.auth import get_user_model
from teams.models import Team

logger = logging.getLogger(__name__)
User = get_user_model

@receiver(post_save, sender=CustomUser)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Handles user creation & profile assignment:
    - Assigns a user to a group based on their role.
    - Creates a profile if it doesn't exist.
    - Saves the profile if updated.
    """
    try:
        # Assign group based on user role
        if created and instance.role in ['student', 'teacher']:
            group_name = 'Students' if instance.role == 'student' else 'Teachers'
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)

        # Ensure profile exists
        profile, profile_created = Profile.objects.get_or_create(user=instance)

        if not profile_created:
            profile.save()  # Update existing profile

    except Exception as e:
        logger.error(f"Error handling profile or group assignment for {instance.username}: {e}")

@receiver(post_save, sender=User)
def update_team_capacity(sender, instance, created, **kwargs):
    """ Recalculate team max_members when a new user is added. """
    if created:  # Only run when a new user is created
        for team in Team.objects.all():
            team.update_max_members()

            