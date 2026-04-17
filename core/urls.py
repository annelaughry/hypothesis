from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from .views import slack_events

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('teams/', include('teams.urls')),  # Instead of views.teams
    path('programs/', include('programs.urls')),
    path('news/', include('news.urls')),
    path('curriculum/', include('curriculum.urls')),
    path('slack/events/', slack_events, name='slack_events'),
]


