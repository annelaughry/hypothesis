from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import get_user_model

from points.models import Points, UserBadge
from news.models import Announcement

User = get_user_model()

BADGES = [
    (1, "🎯 1 Point Club"),
    (2, "🔥 2 Point Milestone"),
    (5, "🏆 5 Point Achiever"),
]

class Command(BaseCommand):
    help = "Checks total points and creates badge announcements for newly earned badges."

    def handle(self, *args, **kwargs):
        # Get total points for each user
        user_points = (
            Points.objects.values('user')
            .annotate(total=Sum('points_earned'))
        )

        for entry in user_points:
            user_id = entry['user']
            total = entry['total']
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                continue

            # ✅ Only give badges to students
            if user.role != "student":
                continue

            for threshold, badge_name in BADGES:
                if total >= threshold:
                    already_awarded = UserBadge.objects.filter(user=user, badge_name=badge_name).exists()
                    if not already_awarded:
                        UserBadge.objects.create(user=user, badge_name=badge_name)

                        Announcement.objects.create(
                            title=f"🎖 Badge Earned: {badge_name}",
                            content=f"{user.username} just earned the **{badge_name}** by reaching {total} points!",
                            type='badge',
                            user=user,
                            badge_name=badge_name
                        )
                        self.stdout.write(f"Awarded {badge_name} to {user.username}")

