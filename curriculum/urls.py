from django.urls import path
from . import views

app_name = "curriculum"

urlpatterns = [
    path("", views.curriculum_home, name="home"),
    path("activity/<int:pk>/edit/", views.activity_edit, name="activity_edit"),
    path("activity/<int:pk>/saved/", views.activity_saved, name="activity_saved"),
    path("activity/<int:pk>/", views.activity_detail, name="activity_detail"),
    path("<slug:slug>/activities/new/", views.activity_create, name="activity_create"),
    path("<slug:slug>/", views.theme_detail, name="theme_detail"),
]
