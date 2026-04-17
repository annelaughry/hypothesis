from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Theme, GuidedResearchActivity
from .forms import GuidedResearchActivityForm, MaterialFormSet, StandardFormSet, FileFormSet


# Curriculum Page View
def curriculum(request):
    return render(request, 'curriculum.html')

def curriculum_home(request):
    themes = Theme.objects.order_by('sort_order', 'name')
    return render(request, 'curriculum/home.html', {'themes': themes})

def theme_detail(request, slug):
    theme = get_object_or_404(Theme, slug=slug)

    guided_activities = theme.guided_activities.filter(is_approved=True)

    user = request.user
    is_teacher_user = (
        user.is_authenticated
        and (
            # main role check
            getattr(user, "role", None) in ["teacher", "admin"]
            # OR helper method if you have it
            or (hasattr(user, "is_teacher") and user.is_teacher())
        )
        and getattr(user, "is_approved", True)
    )

    context = {
        "theme": theme,
        "guided_activities": guided_activities,
        "is_teacher_user": is_teacher_user,
    }
    return render(request, "curriculum/theme_detail.html", context)

def activity_detail(request, pk):
    activity = get_object_or_404(GuidedResearchActivity, pk=pk)

    user = request.user
    is_admin = (
        user.is_authenticated
        and (
            getattr(user, "role", None) == "admin"
            or (hasattr(user, "is_admin") and user.is_admin())
        )
    )

    return render(request, 'curriculum/activity_detail.html', {
        'activity': activity,
        'is_admin': is_admin,
    })

@login_required
def activity_create(request, slug):
    theme = get_object_or_404(Theme, slug=slug)
    user = request.user

    is_teacher_or_admin = (
        getattr(user, "role", None) in ["teacher", "admin"]
        or (hasattr(user, "is_teacher") and user.is_teacher())
    )
    if not is_teacher_or_admin:
        return redirect("curriculum:theme_detail", slug=theme.slug)

    activity = GuidedResearchActivity(theme=theme)

    if request.method == "POST":
        form = GuidedResearchActivityForm(request.POST, instance=activity)
        materials_formset = MaterialFormSet(request.POST, instance=activity)
        standards_formset = StandardFormSet(request.POST, instance=activity)
        file_formset = FileFormSet(request.POST, request.FILES, instance=activity)

        if (
            form.is_valid()
            and materials_formset.is_valid()
            and standards_formset.is_valid()
            and file_formset.is_valid()
        ):
            activity = form.save(commit=False)
            if getattr(user, "role", None) == "admin":
                activity.is_approved = True
            else:
                activity.is_approved = False
            activity.created_by = user
            activity.theme = theme
            activity.save()

            materials_formset.instance = activity
            standards_formset.instance = activity
            file_formset.instance = activity

            materials_formset.save()
            standards_formset.save()
            file_formset.save()

            messages.success(request, "Activity submitted.")
            return redirect("curriculum:theme_detail", slug=theme.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GuidedResearchActivityForm(instance=activity)
        materials_formset = MaterialFormSet(instance=activity)
        standards_formset = StandardFormSet(instance=activity)
        file_formset = FileFormSet(instance=activity)

    return render(
        request,
        "curriculum/activity_form.html",
        {
            "theme": theme,
            "form": form,
            "materials_formset": materials_formset,
            "standards_formset": standards_formset,
            "file_formset": file_formset,
            "is_edit": False,
        },
    )
@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(GuidedResearchActivity, pk=pk)
    theme = activity.theme
    user = request.user

    is_admin = (
        getattr(user, "role", None) == "admin"
        or (hasattr(user, "is_admin") and user.is_admin())
    )
    if not is_admin:
        return redirect("curriculum:activity_detail", pk=activity.pk)

    if request.method == "POST":
        form = GuidedResearchActivityForm(request.POST, instance=activity)
        materials_formset = MaterialFormSet(request.POST, instance=activity)
        standards_formset = StandardFormSet(request.POST, instance=activity)
        file_formset = FileFormSet(request.POST, request.FILES, instance=activity)

        if (
            form.is_valid()
            and materials_formset.is_valid()
            and standards_formset.is_valid()
            and file_formset.is_valid()
        ):
            activity = form.save(commit=False)
            activity.is_approved = True
            activity.save()

            materials_formset.save()
            standards_formset.save()
            file_formset.save()

            return redirect("curriculum:activity_saved", pk=activity.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GuidedResearchActivityForm(instance=activity)
        materials_formset = MaterialFormSet(instance=activity)
        standards_formset = StandardFormSet(instance=activity)
        file_formset = FileFormSet(instance=activity)

    return render(
        request,
        "curriculum/activity_form.html",
        {
            "theme": theme,
            "form": form,
            "materials_formset": materials_formset,
            "standards_formset": standards_formset,
            "file_formset": file_formset,
            "activity": activity,
            "is_edit": True,
        },
    )


@login_required
def activity_saved(request, pk):
    activity = get_object_or_404(GuidedResearchActivity, pk=pk)
    return render(request, "curriculum/activity_saved.html", {"activity": activity})
