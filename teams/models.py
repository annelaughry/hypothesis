from django.db import models
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Sum

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="team_logos/", blank=True, null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='teams_members', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    max_members = models.IntegerField(default=15)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name

    def update_max_members(self):
        User = get_user_model()
        total_users = User.objects.count()
        total_teams = Team.objects.count()

        if total_teams > 0:
            self.max_members = max(1, total_users // total_teams)
            self.save()

    @property
    def total_points(self):
        return self.team_points_from_teams_app.aggregate(
            total_points=Sum("points_earned")
        )["total_points"] or 0

    @admin.display(description='Total Points')
    def display_total_points(self):
        return self.total_points

    @property
    def member_count(self):
        return self.members.count()

    def is_team_full(self):
        return self.members.count() >= self.max_members

    def get_logo_url(self):
        if self.logo:
            return self.logo.url

        filename_png = f"{self.name.lower().replace(' ', '_')}.png"
        filename_jpg = f"{self.name.lower().replace(' ', '_')}.jpg"

        if os.path.exists(os.path.join(settings.MEDIA_ROOT, "team_logos", filename_png)):
            return settings.MEDIA_URL + "team_logos/" + filename_png

        if os.path.exists(os.path.join(settings.MEDIA_ROOT, "team_logos", filename_jpg)):
            return settings.MEDIA_URL + "team_logos/" + filename_jpg

        return settings.STATIC_URL + "default_team_logo.png"

    @property
    def leader(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        top_contributor = (
            self.team_points_from_teams_app
            .values('user')
            .annotate(total=Sum('points_earned'))
            .order_by('-total')
            .first()
        )
        if top_contributor:
            try:
                return User.objects.get(id=top_contributor['user'])
            except User.DoesNotExist:
                return None
        return None


class TeamPoint(models.Model):
    team = models.ForeignKey(
        Team,
        related_name='team_points_from_teams_app',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_points_earned'
    )
    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_points_transferred'
    )
    points_earned = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def transferred_at(self):
        return self.timestamp

    def __str__(self):
        return f"{self.team.name} +{self.points_earned} pts"


@receiver(post_migrate)
def create_default_teams(sender, **kwargs):
    if sender.name == "teams":
        default_teams = [
            "Bunsen Burners", "Capybara", "Fuerza", "Noroc Science",
            "Rocket Riders", "Stealth", "Supernovas", "Parkour Science", "Lab Rats"
        ]
        for team_name in default_teams:
            Team.objects.get_or_create(name=team_name, defaults={"description": f"{team_name} team description"})
        print("✅ Default teams have been created!")
