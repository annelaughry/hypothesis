from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Q
from news.models import Announcement
from points.models import Points
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Generates a monthly announcement for the top 10 teachers."

    def handle(self, *args, **kwargs):
        # Start of current month
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Filter teacher points using reason that indicates teaching
        matches = (
            Points.objects.filter(
                created_at__gte=start_of_month,
                reason__icontains='Approved to teach'  # adjust if needed
            )
            .values('user')
            .annotate(total_points=Sum('points_earned'))
            .order_by('-total_points')[:10]
        )

        if not matches:
            self.stdout.write("No top teachers to display.")
            return

        # Build announcement content
        content_lines = []
        for i, entry in enumerate(matches):
            try:
                user = User.objects.get(id=entry['user'])
                content_lines.append(f"{i+1}. {user.username} — {entry['total_points']} pts")
            except User.DoesNotExist:
                continue

        Announcement.objects.create(
            title="🏫 Top 10 Teachers of the Month",
            content="\n".join(content_lines),
            type='leaderboard'
        )

        self.stdout.write("Created monthly top teachers announcement.")
