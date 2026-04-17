from django.urls import path
from .views import PointsAPIView
from . import views

app_name = 'points'  # Add a namespace

urlpatterns = [
    path('api/points/', PointsAPIView.as_view(), name='api_points'),
    path('levels/', views.level_detail, name='level_detail'),
    path('manage/', views.manage_points_view, name='manage_points'),
    path('add/<int:user_id>/', views.add_points_view, name='add_points'),
    path('deduct/<int:user_id>/', views.deduct_points_view, name='deduct_points'),
    path('points/manage/<int:program_id>/', views.manage_points_view, name='manage_points_program'),

]
