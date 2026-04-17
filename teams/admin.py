from django.contrib import admin
from .models import Team, TeamPoint

class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "logo_preview")

    def logo_preview(self, obj):
        return obj.logo.url if obj.logo else "No Image"

admin.site.register(Team, TeamAdmin)


@admin.register(TeamPoint)
class TeamPointAdmin(admin.ModelAdmin):
    list_display = ('team', 'transferred_by', 'points_earned', 'transferred_at')
    list_filter = ('team',)
    search_fields = ('transferred_by__username', 'team__name')

