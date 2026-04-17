from django.core.management.base import BaseCommand
from teams.models import Team

class Command(BaseCommand):
    help = "Update max_members for all teams based on total users."

    def handle(self, *args, **kwargs):
        teams = Team.objects.all()
        for team in teams:
            team.update_max_members()
            self.stdout.write(self.style.SUCCESS(f'Updated {team.name}: max_members = {team.max_members}'))
