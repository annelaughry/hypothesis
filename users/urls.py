from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from users.views import custom_logout

app_name = "users"

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Profile & User Settings
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_other_view, name='profile_other'),


    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path("avatar_preview/", views.avatar_preview, name="avatar_preview"),  # 👈 Add this line

    path('complete_profile/', views.complete_profile, name='complete_profile'),

    # Dashboards
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),

    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name="password_reset.html",
             email_template_name="password_reset_email.html",  
             success_url='/users/password_reset/done/'
         ), 
         name='password_reset'),

    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name="password_reset_done.html"
         ), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',  
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password_reset_confirm.html",
             success_url='/users/reset/done/'
         ), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="password_reset_complete.html"
         ), 
         name='password_reset_complete'),
    
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('transfer-points/', views.transfer_points_to_team, name='transfer_points_to_team'),


]
