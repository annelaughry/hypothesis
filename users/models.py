from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
import python_avatars as pa
from django.contrib.auth import get_user_model
import python_avatars
import io
from django.core.files.base import ContentFile
from teams.models import Team
from datetime import timedelta, date
from django.utils.timezone import now


# Custom User Model
class CustomUser(AbstractUser):
    team = models.ForeignKey(
        'teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name="users_team"
    )
    team_join_deadline = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.team_join_deadline:  # Set deadline only on first save
            self.team_join_deadline = now().date() + timedelta(days=30)
        super().save(*args, **kwargs)

    def has_team_join_expired(self):
        """Check if the deadline to join a team has expired."""
        return self.team_join_deadline and now().date() > self.team_join_deadline

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    LEVEL_CHOICES = [
        ('explorer', 'Explorer'),
        ('ambassador', 'Ambassador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)  # only for students
    is_approved = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)  # new field to track completions

    ysa_way_passed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'
    

User = get_user_model()


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    points = models.PositiveIntegerField(default=0)
    points_transferred = models.PositiveIntegerField(default=0)    
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="team_profile")
    team_joined = models.BooleanField(default=False)
    join_deadline = models.DateField(null=True, blank=True)

    # Personal Information
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    school = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    profile_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Avatar Upload & Customization
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)  # Uploaded avatar
    generated_avatar = models.ImageField(upload_to="generated_avatars/", blank=True, null=True)  # SVG avatar
    pip_quote = models.CharField(max_length=150, blank=True, null=True, help_text="A pip for your profile!")
    
    # Avatar Customization Choices
    background_color = models.CharField(
        max_length=20, choices=[(tag.name, tag.value) for tag in pa.BackgroundColor], default="WHITE"
    )
    hair_type = models.CharField(
        max_length=30, choices=[(tag.name, tag.value) for tag in pa.HairType], default="BOB"
    )
    hair_color = models.CharField(
        max_length=20, choices=[(tag.name, tag.value) for tag in pa.HairColor], default="BROWN"
    )
    eye_type = models.CharField(
        max_length=20, choices=[(tag.name, tag.value) for tag in pa.EyeType], default="DEFAULT"
    )
    mouth_type = models.CharField(
        max_length=20, choices=[(tag.name, tag.value) for tag in pa.MouthType], default="SMILE"
    )
    accessory = models.CharField(
        max_length=20, choices=[(tag.name, tag.value) for tag in pa.AccessoryType], default="NONE"
    )
    clothing = models.CharField(
        max_length=30, choices=[(tag.name, tag.value) for tag in pa.ClothingType], default="HOODIE"
    )
    clothing_color = models.CharField(
        max_length=20, choices=[(tag.name, tag.value) for tag in pa.ClothingColor], default="PASTEL_GREEN"
    )
    shirt_text = models.CharField(max_length=20, blank=True, null=True)

    def generate_avatar(self):
        """Generates an avatar using user-selected customization options."""
        avatar = pa.Avatar(
            style=pa.AvatarStyle.TRANSPARENT,
            background_color=getattr(pa.BackgroundColor, self.background_color, pa.BackgroundColor.WHITE),
            top=getattr(pa.HairType, self.hair_type, pa.HairType.BOB),
            hair_color=getattr(pa.HairColor, self.hair_color, pa.HairColor.BROWN),
            eyes=getattr(pa.EyeType, self.eye_type, pa.EyeType.DEFAULT),
            mouth=getattr(pa.MouthType, self.mouth_type, pa.MouthType.SMILE),
            accessory=getattr(pa.AccessoryType, self.accessory, pa.AccessoryType.NONE),
            clothing=getattr(pa.ClothingType, self.clothing, pa.ClothingType.HOODIE),
            clothing_color=getattr(pa.ClothingColor, self.clothing_color, pa.ClothingColor.PASTEL_GREEN),
            shirt_text=self.shirt_text,
        )

        avatar_svg = avatar.render()  # Generate SVG output
        self.generated_avatar.save(f"{self.user.username}_avatar.svg", ContentFile(avatar_svg.encode("utf-8")), save=False)
        self.save()

    def has_avatar(self):
        """Check if the user has either an uploaded or generated avatar."""
        return bool(self.avatar or self.generated_avatar)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def update_points(self):
        """Recalculates and updates the total points for the user."""
        total_points = self.user.points_set.aggregate(total=models.Sum('points_earned'))['total'] or 0
        self.points = total_points
        self.save()

    @property
    def short_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name[0]}"
        return self.first_name
    


# Signals to Create Profile on User Creation
@receiver(post_save, sender=CustomUser)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


# Signal to Create Default Groups
@receiver(post_migrate)
def create_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Teacher')
    Group.objects.get_or_create(name='Student')



