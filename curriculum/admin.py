from django.contrib import admin
from .models import (
    Theme,
    GuidedResearchActivity,
    ResearchMaterial,
    ResearchStandard,
    Standard,
)

class MaterialInline(admin.TabularInline):
    model = ResearchMaterial
    extra = 1


class StandardInline(admin.TabularInline):
    model = ResearchStandard
    extra = 1


# ----- Theme admin -----

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


# ----- GuidedResearchActivity admin (with inlines) -----

@admin.register(GuidedResearchActivity)
class GuidedResearchActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "theme", "created_by", "is_approved", "created_at")
    list_filter = ("theme", "is_approved")
    search_fields = ("title", "overview", "objectives")
    inlines = [MaterialInline, StandardInline]
    actions = ["approve_activities"]

    def approve_activities(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} activity(ies) approved.")
    approve_activities.short_description = "Approve selected activities"


# (Optional) You can register these too if you want them separately visible in admin,
# but it's not required if you only edit them via inlines.

@admin.register(ResearchMaterial)
class ResearchMaterialAdmin(admin.ModelAdmin):
    list_display = ("text", "activity")
    list_filter = ("activity",)


@admin.register(ResearchStandard)
class ResearchStandardAdmin(admin.ModelAdmin):
    list_display = ("text", "activity")
    list_filter = ("activity",)


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ("framework", "code", "grade_band", "subject", "active")
    list_filter = ("framework", "grade_band", "subject", "active")
    search_fields = ("code", "description")
    ordering = ("framework", "code")