from django.urls import include, path
from .migrations import views

urlpatterns = [
    path('github-webhook/', views.github_webhook, name='github-webhook'),
]
