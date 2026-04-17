from django.db import models
from django.conf import settings

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('leaderboard', 'Leaderboard'),
        ('badge', 'Badge Earned'),
        ('program', 'Program Update'),
        ('team', 'Team Update'),
        ('class_notice', 'Class Notice'),
        ('custom', 'Custom'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='custom')
    created_at = models.DateTimeField(auto_now_add=True)
    display_start = models.DateTimeField(null=True, blank=True)
    display_end = models.DateTimeField(null=True, blank=True)
    pinned = models.BooleanField(default=False)

    # Optional references for automation
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    program = models.ForeignKey('programs.Program', null=True, blank=True, on_delete=models.SET_NULL)
    team = models.ForeignKey('teams.Team', null=True, blank=True, on_delete=models.SET_NULL)
    badge_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
    

class HighFive(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    announcement = models.ForeignKey("Announcement", on_delete=models.CASCADE, related_name="highfives")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'announcement')  # One high five per user per announcement

