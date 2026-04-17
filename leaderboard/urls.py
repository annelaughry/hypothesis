from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path('', views.student_leaderboard, name='student_leaderboard'),  # This becomes the landing
    path('students/', views.student_leaderboard, name='student_leaderboard'),
    path('teams/', views.team_leaderboard, name='leaderboard_team'),
]
