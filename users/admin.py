from django.contrib import admin
from .models import Profile, CustomUser


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'points', 'school')
    list_filter = ('school',)
    search_fields = ('user__username', 'first_name', 'last_name')
    ordering = ('user',)  # FIXED: Ordering by user instead of user__username
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_approved', 'role', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_approved', 'role', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('username', 'date_joined')  # FIXED: Added `date_joined` for better sorting
    list_per_page = 50

    # FIXED: Ensure fields exist before making them readonly
    readonly_fields = ('date_joined', 'last_login') if hasattr(CustomUser, 'date_joined') and hasattr(CustomUser, 'last_login') else ()

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_approved', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
