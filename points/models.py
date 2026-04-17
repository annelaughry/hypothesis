from django.utils.timezone import now
from django.db import models
from django.forms import ValidationError
from django.conf import settings
from teams.models import Team
from users.models import CustomUser

class Points(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='points_set')
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, related_name='team_points')
    program = models.ForeignKey('programs.Program', null=True, blank=True, on_delete=models.CASCADE, related_name='program_points')
    
    # Add distinct related_name to avoid conflict
    activity = models.ForeignKey('programs.Activity', null=True, blank=True, on_delete=models.CASCADE, related_name='activity_point_logs')
    step = models.ForeignKey('programs.ActivityStep', null=True, blank=True, on_delete=models.CASCADE, related_name='step_point_logs')
    
    points_earned = models.IntegerField(default=0)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} earned {self.points_earned} points for: {self.reason}"



class IndividualPoints(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="individual_points")
    points = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} individual points"

    class Meta:
        verbose_name = "Individual Points"
        verbose_name_plural = "Individual Points"


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge_name = models.CharField(max_length=255)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge_name')

    def __str__(self):
        return f"{self.user.username} - {self.badge_name}"
