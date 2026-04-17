from django.shortcuts import render, redirect
from users.models import CustomUser
from teams.models import Team
from points.models import IndividualPoints, Points
from django.db.models import Sum
from django.templatetags.static import static


def leaderboard_home(request):
    return redirect('leaderboard:student_leaderboard')


def student_leaderboard(request):
    # Step 1: get students ordered by total points
    students = (
        CustomUser.objects.filter(role='student')
        .annotate(total_points=Sum('points_set__points_earned'))
        .filter(total_points__gt=0)
        .select_related('team', 'profile')
        .order_by('-total_points')
    )

    # Step 2: annotate each student's avatar_url safely
    for student in students:
        profile = student.profile
        if profile.avatar:
            student.avatar_url = profile.avatar.url
        elif profile.generated_avatar:
            student.avatar_url = profile.generated_avatar.url
        else:
            student.avatar_url = static('images/default_avatar.png')

    return render(request, 'student_leaderboard.html', {
        'students': students,
        'view_name': 'student_leaderboard'
    })



def team_leaderboard(request):
    teams = Team.objects.all()

    for team in teams:
        # top 3 students
        team.top_students = (
            CustomUser.objects
            .filter(team=team)
            .annotate(total_points=Sum('points_set__points_earned'))
            .order_by('-total_points')[:3]
        )

        # all members with point totals
        team.all_members = (
            CustomUser.objects
            .filter(team=team)
            .annotate(total_points=Sum('points_set__points_earned'))
            .order_by('-total_points')
        )

    return render(request, 'leaderboard_team.html', {'teams': teams})


