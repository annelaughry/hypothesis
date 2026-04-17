from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import  StartProjectForm, BackgroundResearchForm, ResearchQuestionsForm, HypothesisForm, ExperimentalDesignForm

from .models import BackgroundResearch, Project, ResearchQuestions, Hypothesis, ExperimentalDesign, GroupMember


def _get_or_create_active_project(user):
    project = Project.objects.filter(owner=user, is_active=True).first()
    if not project:
        project = Project.objects.create(owner=user, title="My Research Project")
    return project


@login_required
def home(request):
    """Homepage with a clear call to action to start a project."""
    # If the user already has an active project, show its title and a continue button
    project = Project.objects.filter(owner=request.user, is_active=True).first()
    return render(request, "project_planner/home.html", {"project": project})


@login_required
def start_project(request):
    """Collect project title and group member names, create the project, and redirect to step 1."""
    if request.method == "POST":
        form = StartProjectForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip() or "Untitled Project"
            member_lines = form.cleaned_data.get("member_names", "").splitlines()

            # Deactivate any previous active projects for this user
            Project.objects.filter(owner=request.user, is_active=True).update(is_active=False)

            project = Project.objects.create(owner=request.user, title=title, is_active=True)

            # Parse members: allow "Name <email>" or just "Name"
            for line in member_lines:
                line = line.strip()
                if not line:
                    continue
                name, email = line, ""
                if "<" in line and ">" in line:
                    # crude parse like: Alex Lee <alex@example.com>
                    name = line.split("<", 1)[0].strip()
                    email = line.split("<", 1)[1].split(">", 1)[0].strip()
                GroupMember.objects.create(project=project, name=name, email=email)

            messages.success(request, "Project created. Let's start Background Research.")
            return redirect("project_planner:background_research_edit")
    else:
        form = StartProjectForm()

    return render(request, "project_planner/start_project.html", {"form": form})


@login_required
def background_research_edit(request):
    project = _get_or_create_active_project(request.user)
    section, _ = BackgroundResearch.objects.get_or_create(project=project)

    if request.method == "POST":
        form = BackgroundResearchForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Background Research saved.")
            return redirect("project_planner:background_research_edit")
    else:
        form = BackgroundResearchForm(instance=section)

    return render(request, "project_planner/background_research_form.html", {"form": form, "project": project})


@login_required
def research_questions_edit(request):
    project = _get_or_create_active_project(request.user)
    section, _ = ResearchQuestions.objects.get_or_create(project=project)

    if request.method == "POST":
        form = ResearchQuestionsForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Research Question section saved.")
            return redirect("project_planner:research_questions_edit")
    else:
        form = ResearchQuestionsForm(instance=section)

    return render(request, "project_planner/research_question_form.html", {"form": form, "project": project})


@login_required
def hypothesis_edit(request):
    project = _get_or_create_active_project(request.user)
    section, _ = Hypothesis.objects.get_or_create(project=project)

    if request.method == "POST":
        form = HypothesisForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Hypothesis section saved.")
            return redirect("project_planner:hypothesis_edit")
    else:
        form = HypothesisForm(instance=section)

    return render(request, "project_planner/hypothesis_form.html", {"form": form, "project": project})

@login_required
def experimental_design_edit(request):
    project = _get_or_create_active_project(request.user)
    section, _ = ExperimentalDesign.objects.get_or_create(project=project)

    if request.method == "POST":
        # files must be passed to handle setup_image
        form = ExperimentalDesignForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Experimental Design section saved.")
            return redirect("project_planner:experimental_design_edit")
    else:
        form = ExperimentalDesignForm(instance=section)

    return render(request, "project_planner/experimental_design_form.html", {"form": form, "project": project})



@staff_member_required
def project_document_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not request.user.is_staff:
        raise Http404
    return render(
        request,
        "project_planner/project_document.html",
        {
            "project": project,
            "bg": getattr(project, "background_research", None),
            "rq": getattr(project, "research_questions", None),
            "hyp": getattr(project, "hypothesis", None),
            "exp": getattr(project, "experimental_design", None),
        },
    )
