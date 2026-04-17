"""
URL configuration for pippet_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pippet_project/urls.py

# pippet_project/urls.py

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from core.views import home
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),  # Core app handles homepage
    path('teams/', include('teams.urls', namespace='teams')),  # Ensure namespace is set
    path('programs/', include('programs.urls', namespace='programs')),
    path('news/', include('news.urls', namespace='news')),
    path('curriculum/', include('curriculum.urls', namespace='curriculum')),
    path('users/', include('users.urls', namespace='users')),

    path('', home, name='home'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('points/', include('points.urls', namespace='points')),

    path('leaderboard/', include('leaderboard.urls')),
    path('foodwaste/', include("foodwaste.urls", namespace="foodwaste")),
    path('classrooms/', include('classrooms.urls', namespace='classrooms')),
    path('curriculum/', include('curriculum.urls', namespace='curriculum')),
    path('planner/', include('project_planner.urls', namespace='project_planner')),


    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



