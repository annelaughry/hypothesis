from django.contrib import admin
from .models import Points, IndividualPoints

@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'team',
        'program',
        'activity',
        'step',
        'points_earned',
        'reason',
        'created_at',
    )
    list_filter = ('team', 'program', 'created_at')
    search_fields = ('user__username', 'team__name', 'program__name', 'reason')


@admin.register(IndividualPoints)
class IndividualPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'date_added')
    search_fields = ('user__username',)
    list_filter = ('date_added',)
