from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'created_at', 'pinned')
    list_filter = ('type', 'pinned', 'created_at')
    search_fields = ('title', 'content', 'badge_name')
