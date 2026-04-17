from django.contrib import admin
from .models import (
    Theme,
    Program,
    Activity,
    ProgramRegistration,
    TeachingRequest,
    YSAWayTest,
    GuidedActivity,
    ActivityStep,
    InvestigationProcedure,
    ProgramCreationRequest,
    ActivityTimeline,
    Goal,
    Dataset,
    DataRow
)

# 🧠 Theme Admin
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'background_image')

# 📘 Program Admin
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_approved_teachers', 'is_approved', 'theme')
    list_filter = ('is_approved', 'theme')
    search_fields = ('name', 'description')

    def get_approved_teachers(self, obj):
        approved_teachers = obj.teaching_requests.filter(is_approved=True).values_list('teacher__username', flat=True)
        return ", ".join(approved_teachers) if approved_teachers else "—"
    get_approved_teachers.short_description = 'Approved Teachers'

# 🧪 Activity Admin
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'points')
    list_filter = ('program',)
    search_fields = ('title', 'description')

# 🔬 ActivityStep Admin
@admin.register(ActivityStep)
class ActivityStepAdmin(admin.ModelAdmin):
    list_display = ('step_key', 'step_type', 'order', 'points', 'activity')
    list_filter = ('step_key', 'step_type', 'activity')
    search_fields = ('instructions', 'question')

# 👩‍🎓 Program Registration Admin
@admin.register(ProgramRegistration)
class ProgramRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'program', 'start_date', 'end_date', 'is_approved', 'registered_at' )
    list_filter = ('is_approved', 'registered_at')
    search_fields = ('student__username', 'program__name')

# 👨‍🏫 Teaching Request Admin
@admin.register(TeachingRequest)
class TeachingRequestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'program', 'start_date', 'end_date', 'is_approved', 'requested_at')
    list_filter = ('is_approved', 'requested_at')
    search_fields = ('teacher__username', 'program__name')

# ✅ YSA Way Test Admin
@admin.register(YSAWayTest)
class YSAWayTestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'has_passed', 'completed_at')
    list_filter = ('has_passed',)
    search_fields = ('teacher__username',)

# 🧭 Guided Activity Admin
@admin.register(GuidedActivity)
class GuidedActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'program')
    search_fields = ['title']

# 🧪 Investigation Procedure Admin
@admin.register(InvestigationProcedure)
class InvestigationProcedureAdmin(admin.ModelAdmin):
    list_display = ('program',)
    search_fields = ('program__name',)

# request create program Admin
@admin.register(ProgramCreationRequest)
class ProgramCreationRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'requested_at', 'is_approved')
    list_filter = ('is_approved', 'requested_at')
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        for req in queryset:
            if not req.is_approved:
                req.is_approved = True
                req.save()
                # Optionally, auto-create a Program here
        self.message_user(request, "Selected requests approved.")

@admin.register(ActivityTimeline)
class ActivityTimelineAdmin(admin.ModelAdmin):
    list_display = ('activity', 'teacher', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'teacher')
    search_fields = ('activity__title', 'teacher__username', 'teacher__email')
    autocomplete_fields = ['activity', 'teacher']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug')


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal', 'created_at')
    list_filter = ('goal',)
    search_fields = ('name', 'goal__title')

@admin.register(DataRow)
class DataRowAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'id')
    search_fields = ('dataset__name',)