import datetime
import json
import hmac
import hashlib
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.core.paginator import Paginator
import python_avatars as pa
from django.utils.timezone import now
from .forms import SignupForm, StudentProfileForm, TeacherProfileForm, ProfileForm, AvatarCustomizationForm
from .models import CustomUser, Profile
from core.slack_utils import send_slack_notification
from points.models import Points
from news.models import Announcement
from django.core.files.base import ContentFile
from programs.models import ProgramRegistration, TeachingRequest, EditRequest, StepResponse, ActivityTimeline
from teams.models import TeamPoint
from programs.models import StepResponse, ProgramCreationRequest, ActivityStep, ActivityTimeline  # or wherever your StepResponse model is
from django.db.models import Sum
from django.db import models
from points.models import UserBadge
from points.utils import get_user_level, points_to_next_level
from datetime import date
from django.utils import timezone
from django.views.decorators.http import require_POST



# LOGIN

def calculate_untransferred_points(user):
    total_earned = StepResponse.objects.filter(student=user).aggregate(
        total=Sum("step__points")
    )["total"] or 0

    transferred = user.profile.points_transferred or 0
    return max(total_earned - transferred, 0)

def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid username.')
            return render(request, 'login.html', {'form': form})

        # Only enforce approval for teacher/admin accounts
        if user.role in ['teacher', 'admin'] and not user.is_approved:
            messages.error(request, 'Your account is pending approval.')
            return render(request, 'login.html', {'form': form})


        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid password.')
            return render(request, 'login.html', {'form': form})

    return render(request, 'login.html', {'form': form})

# LOGOUT

def custom_logout(request):
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("users:login")

# SIGNUP

def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])

        # Decide approval based on role
        role = user.role  

        if role in ['teacher', 'admin']:
            # Require approval
            user.is_active = False          # cannot log in yet
            user.is_approved = False
            needs_approval = True
        else:
            # Student: auto-approved
            user.is_active = True           # allow login
            user.is_approved = True
            needs_approval = False

        user.save()

        if role == 'teacher':
            classroom = Classroom.objects.create(
                name=f"{user.username}'s Classroom",
                code=user.username[:4].upper() + '1234',  # or a better random code
                owner=user,
            )
            Membership.objects.create(user=user, classroom=classroom, role='teacher')

        if needs_approval:
            # Only notify + show "waiting for approval" for teacher/admin
            send_slack_notification('new_signup', user.username, 'approval_needed')
            messages.success(request, 'Account created! Please wait for approval.')
        else:
            messages.success(request, 'Account created! You can log in now.')

        return redirect('users:login')

    return render(request, 'signup.html', {'form': form})


# PROFILE VIEW

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)

    # Total points
    total_points = Points.objects.filter(user=request.user).aggregate(total=Sum("points_earned"))["total"] or 0

    # Badges earned
    BADGE_STYLES = {
            "🎯 1 Point Club": {"emoji": "🎯", "tier": "bronze"},
            "🔥 2 Point Milestone": {"emoji": "🔥", "tier": "silver"},
            "🏆 5 Point Achiever": {"emoji": "🏆", "tier": "gold"},
        }

        # Enhance badge list
    badges_raw = UserBadge.objects.filter(user=request.user).order_by('-awarded_at')

    badges = []
    for badge in badges_raw:
            style = BADGE_STYLES.get(badge.badge_name, {})
            badges.append({
                "name": badge.badge_name,
                "emoji": style.get("emoji", "🏅"),
                "tier": style.get("tier", "default"),
                "awarded_at": badge.awarded_at
            })

        # Return in context
    return render(request, 'profile.html', {
        'profile': profile,
        'points': total_points,
        'badges': badges
        })

def profile_other_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    profile = user.profile  # Assuming one-to-one relation exists

    context = {
        'user_profile': profile,
        'other_user': user,
    }
    return render(request, 'profile_other.html', context)

# EDIT PROFILE

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        avatar_form = AvatarCustomizationForm(request.POST, instance=profile)

        def get_enum_value(enum_class, value, default):
            if value and hasattr(enum_class, value.upper()):
                return getattr(enum_class, value.upper())
            return getattr(enum_class, default)

        if "avatar" in request.FILES:
            # User uploaded an avatar, use that
            profile.generated_avatar = None
            if form.is_valid():
                form.save()
            return redirect("users:edit_profile")

        if form.is_valid() and avatar_form.is_valid():
            # User customized avatar – generate new image
            custom_avatar = pa.Avatar(
                top=get_enum_value(pa.HairType, avatar_form.cleaned_data.get("hair_type"), "SHORT"),
                hair_color=get_enum_value(pa.HairColor, avatar_form.cleaned_data.get("hair_color"), "BROWN"),
                skin_color=get_enum_value(pa.SkinColor, avatar_form.cleaned_data.get("skin_color"), "PALE"),
                clothing=get_enum_value(pa.ClothingType, avatar_form.cleaned_data.get("clothing_type"), "HOODIE"),
                clothing_color=get_enum_value(pa.ClothingColor, avatar_form.cleaned_data.get("clothing_color"), "BLACK"),
                facial_hair=get_enum_value(pa.FacialHairType, avatar_form.cleaned_data.get("facial_hair"), "NONE"),
                eyes=get_enum_value(pa.EyeType, avatar_form.cleaned_data.get("eyes"), "DEFAULT"),
                eyebrows=get_enum_value(pa.EyebrowType, avatar_form.cleaned_data.get("eyebrows"), "FLAT_NATURAL"),
                mouth=get_enum_value(pa.MouthType, avatar_form.cleaned_data.get("mouth"), "SMILE"),
                accessory=get_enum_value(pa.AccessoryType, avatar_form.cleaned_data.get("accessory"), "NONE"),
                shirt_graphic=pa.ClothingGraphic.CUSTOM_TEXT,
                shirt_text=avatar_form.cleaned_data.get("shirt_text", ""),
            )
            avatar_svg = custom_avatar.render()
            avatar_file = ContentFile(avatar_svg.encode("utf-8"), name=f"{request.user.username}_avatar.svg")
            profile.avatar = None  # remove uploaded one if switching back
            profile.generated_avatar.save(avatar_file.name, avatar_file, save=True)
            form.save()
            profile.save()
            request.user.profile_completed = True
            request.user.save()

            if request.user.role == "student":
                return redirect("users:student_dashboard")
            elif request.user.role == "teacher":
                return redirect("users:teacher_dashboard")
            else:
                return redirect("users:profile")

    else:
        form = ProfileForm(instance=profile)
        avatar_form = AvatarCustomizationForm(instance=profile)

    return render(request, "edit_profile.html", {
        "form": form,
        "avatar_form": avatar_form,
        "profile": profile,
    })


@require_POST
@csrf_exempt
def avatar_preview(request):
    form = AvatarCustomizationForm(request.POST)
    if form.is_valid():
        avatar = pa.Avatar(
            top=pa.HairType[form.cleaned_data['hair_type'].upper()],
            hair_color=pa.HairColor[form.cleaned_data['hair_color'].upper()],
            skin_color=pa.SkinColor[form.cleaned_data['skin_color'].upper()],
            clothing=pa.ClothingType[form.cleaned_data['clothing_type'].upper()],
            clothing_color=pa.ClothingColor[form.cleaned_data['clothing_color'].upper()],
            facial_hair=pa.FacialHairType[form.cleaned_data['facial_hair'].upper()],
            eyes=pa.EyeType[form.cleaned_data['eyes'].upper()],
            eyebrows=pa.EyebrowType[form.cleaned_data['eyebrows'].upper()],
            mouth=pa.MouthType[form.cleaned_data['mouth'].upper()],
            accessory=pa.AccessoryType[form.cleaned_data['accessory'].upper()],
            shirt_graphic=pa.ClothingGraphic.CUSTOM_TEXT,
            shirt_text=form.cleaned_data.get("shirt_text", ""),
        )
        svg = avatar.render()
        return HttpResponse(svg, content_type="image/svg+xml")
    return HttpResponse("Invalid data", status=400)



# COMPLETE PROFILE

@login_required
def complete_profile(request):
    user = request.user
    if user.profile_completed:
        return redirect('users:student_dashboard' if user.role == 'student' else 'users:teacher_dashboard')
    form = StudentProfileForm(request.POST, instance=user.profile) if user.role == 'student' else TeacherProfileForm(request.POST, instance=user.profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        user.profile_completed = True
        user.save()
        return redirect('users:student_dashboard' if user.role == 'student' else 'users:teacher_dashboard')
    return render(request, 'complete_profile.html', {'form': form})

# TEACHER DASHBOARD

@login_required
@user_passes_test(lambda user: user.role == 'teacher', login_url='core:home')
def teacher_dashboard(request):
    if not request.user.profile_completed:
        return redirect('users:edit_profile')

    profile = request.user.profile
    announcements = Announcement.objects.all().order_by('-created_at')
    paginator = Paginator(announcements, 5)
    page_number = request.GET.get('page')

    # Approved teaching programs
    approved_programs = [r.program for r in TeachingRequest.objects.filter(
        teacher=request.user,
        is_approved=True
    ).select_related('program')]

    # 🆕 Total points from centralized Points model
    total_points = Points.objects.filter(user=request.user).aggregate(total=models.Sum("points_earned"))["total"] or 0
    progress_width = min(total_points, 100)  # Or scale as needed

    return render(request, 'teacher_dashboard.html', {
        'announcements': paginator.get_page(page_number),
        'approved_programs': approved_programs,
        'profile': profile,
        'points': total_points,
        'progress_width': progress_width,
    })

# STUDENT DASHBOARD

@login_required
def student_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    # Approved programs the student is registered for
    approved_registrations = ProgramRegistration.objects.select_related('program').filter(
        student=request.user,
        is_approved=True
    )

    registered_programs_with_progress = []

    for reg in approved_registrations:
        program = reg.program
        activities = program.guided_activities.all()
        total_steps = ActivityStep.objects.filter(activity__in=activities).count()
        completed_steps = StepResponse.objects.filter(
            step__activity__in=activities,
            student=request.user
        ).count()
        progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0

        registered_programs_with_progress.append({
            'program': program,
            'progress': progress,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
        })

    # Total points
    total_points = Points.objects.filter(user=request.user).aggregate(
        total=Sum('points_earned')
    )['total'] or 0

    # Level and next level info
    level_info = get_user_level(total_points)
    remaining_points, next_level_name = points_to_next_level(total_points)

    # Determine level cap for progress bar
    if total_points < 100:
        level_cap = 100
    elif total_points < 400:
        level_cap = 400
    elif total_points < 600:
        level_cap = 600
    else:
        level_cap = total_points + 100

    progress_width = min(int((total_points / level_cap) * 100), 100)

    deadline_warnings = []

    for reg in approved_registrations:
        program = reg.program
        activities = program.guided_activities.all()
        timelines = ActivityTimeline.objects.filter(
            activity__in=activities,
            end_date__isnull=False,
            end_date__gte=timezone.now().date()
        ).select_related('activity', 'activity__program')

        for timeline in timelines:
            days_left = (timeline.end_date - timezone.now().date()).days
            deadline_warnings.append({
                'activity': timeline.activity,
                'program': timeline.activity.program,
                'end_date': timeline.end_date,
                'days_left': days_left
            })

    # Sort by soonest deadline
    deadline_warnings.sort(key=lambda x: x['end_date'])

    return render(request, 'student_dashboard.html', {
        'profile': profile,
        'registered_programs': registered_programs_with_progress,  # ← updated
        'points': total_points,
        'progress_width': progress_width,
        'level_info': level_info,
        'remaining_points': remaining_points,
        'next_level_name': next_level_name,
        'classes': [],
        'deadline_warnings': deadline_warnings,

    })



# ADMIN APPROVAL

@login_required
@user_passes_test(lambda user: user.is_staff, login_url='core:home')
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.is_approved = True
        user.is_active = True
        user.save()
        send_slack_notification('approval', user.username, 'account_approved')
        messages.success(request, f"User {user.username} approved.")
        return redirect('admin_dashboard')
    return render(request, 'approve_user.html', {'user': user})

# ADMIN DASHBOARD

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    registrations = ProgramRegistration.objects.filter(is_approved=False)
    teaching_requests = TeachingRequest.objects.filter(is_approved=False)
    edit_requests = EditRequest.objects.filter(is_approved=False)
    program_creation_requests = ProgramCreationRequest.objects.filter(is_approved=False)

    return render(request, "admin_dashboard.html", {
        "registrations": registrations,
        "teaching_requests": teaching_requests,
        "edit_requests": edit_requests,
        "program_creation_requests": program_creation_requests,
    })

def calculate_untransferred_points(user):
    # Use centralized Points model for everyone
    total_earned = Points.objects.filter(user=user).aggregate(
        total=Sum("points_earned")
    )["total"] or 0

    transferred = user.profile.points_transferred or 0
    return max(total_earned - transferred, 0)

@login_required
def transfer_points_to_team(request):
    user = request.user
    profile = user.profile

    redirect_url = "users:student_dashboard" if user.role == "student" else "users:teacher_dashboard"

    # Ensure user has a team
    if not user.team:
        messages.error(request, "You must join a team before transferring points.")
        return redirect(redirect_url)

    if request.method == "POST":
        untransferred = calculate_untransferred_points(user)

        if untransferred <= 0:
            messages.warning(request, "No untransferred points available.")
            return redirect(redirect_url)

        user.team.team_points_from_teams_app.create(
            points_earned=untransferred,
            user=user,
            transferred_by=user
        )

        profile.points_transferred += untransferred
        profile.save()

        role_msg = "student" if user.role == "student" else "teacher"
        messages.success(request, f"As a {role_msg}, you transferred {untransferred} points to your team!")
        return redirect(redirect_url)

    return redirect(redirect_url)


