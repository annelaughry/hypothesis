from django.urls import path
from . import views

app_name = "foodwaste"

urlpatterns = [
    path('', views.home_view, name='home'),  # This is the homepage URL
    path('input/', views.food_entry_view, name='food_entry'),
    path('report/', views.report_view, name='report'),
    path('submissions/', views.full_report_view, name='full_report'),

]
