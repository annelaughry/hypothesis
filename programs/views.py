from io import TextIOWrapper
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from users.views import is_admin
from users.models import CustomUser
from .models import (
    Theme, Program, ProgramRegistration, 
    TeachingRequest, EditRequest, Activity, 
    GuidedActivity, ActivityStep, StepResponse, 
    InvestigationProcedure, StepOption, 
    ProgramCreationRequest, ActivityTimeline, Goal,
    Dataset, DataRow)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static
from django.db.models import Exists, OuterRef
from .forms import (ProgramForm, ActivityForm, 
GuidedActivityForm, ActivityStepForm, StepResponseForm, 
InvestigationProcedureForm, StepOptionFormSet, 
ActivityTimelineForm, DatasetForm, DataRowForm)
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory
from points.models import Points 
from django.utils.timezone import now
from django.db.models import Sum 
from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from datetime import date
from django.template.loader import select_template
import csv

#-----------------------------------------------------------------
#switching to goals instead of themes:

def goal_list(request):
    goals = Goal.objects.all()
    return render(request, 'goal_list.html', {'goals': goals})

def goal_detail(request, slug):
    goal = get_object_or_404(Goal, slug=slug)

    # Try to load a custom template for the goal
    template_choices = [
        f"goals/{goal.slug}_detail.html",  # e.g., climate-action_detail.html
        "goal_detail.html"  # fallback
    ]
    template = select_template(template_choices)

    return render(request, template.template.name, {'goal': goal})

def explore_science(request, slug):
    goal = get_object_or_404(Goal, slug=slug)
    programs = Program.objects.filter(goal=goal).prefetch_related('activities')
    return render(request, 'explore_science.html', {
        'goal': goal,
        'programs': programs
    })

def plan_project(request, slug):
    goal = get_object_or_404(Goal, slug=slug)
    return render(request, 'plan_project.html', {'goal': goal})


def create_dataset(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save()
            if dataset.uploaded_csv:
                csvfile = TextIOWrapper(dataset.uploaded_csv.file, encoding='utf-8')
                reader = csv.DictReader(csvfile)
                for row in reader:
                    DataRow.objects.create(dataset=dataset, data=row)
            return redirect('goals:goal_detail', pk=dataset.goal.pk)
    else:
        form = DatasetForm()
    return render(request, 'create_dataset.html', {'form': form})

def goal_dataset_list(request, slug):
    goal = get_object_or_404(Goal, slug=slug)
    datasets = goal.datasets.all()
    return render(request, "goal_dataset_list.html", {
        "goal": goal,
        "datasets": datasets,
    })

def dataset_detail(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    rows = dataset.rows.all()

    # Dynamically get all column keys from the data
    columns = set()
    for row in rows:
        columns.update(row.data.keys())
    columns = sorted(columns)

    return render(request, 'dataset_detail.html', {
        'dataset': dataset,
        'rows': rows,
        'columns': columns
    })
def is_teacher_or_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'teacher'

@login_required
@user_passes_test(is_teacher_or_admin)
def edit_dataset(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    DataRowFormSet = modelformset_factory(DataRow, fields=('data',), extra=1, can_delete=True)

    if request.method == 'POST':
        formset = DataRowFormSet(request.POST, queryset=dataset.rows.all())
        if formset.is_valid():
            rows = formset.save(commit=False)
            for row in rows:
                row.dataset = dataset
                row.save()
            for deleted in formset.deleted_objects:
                deleted.delete()
            messages.success(request, "Dataset updated successfully.")
            return redirect('programs:dataset_detail', pk=pk)
    else:
        formset = DataRowFormSet(queryset=dataset.rows.all())

    return render(request, 'edit_dataset.html', {
        'dataset': dataset,
        'formset': formset
    })

#-----------------------------------------------------------------

# 🆕 1. List all themes
def theme_list(request):
    themes = Theme.objects.all()
    for theme in themes:
        # Unlock YSA Way by default
        if theme.name.lower() == "ysa way":
            theme.locked = False
        # ✅ TEMP: Unlock only "Atmosphere" for testing
        elif theme.name.lower() == "atmosphere" and request.user.username == "test":
            theme.locked = False
        else:
            theme.locked = theme.is_locked_for_user(request.user)
        
        # Match image based on name
        filename = theme.name.lower().replace(' ', '_') + '.jpg'
        theme.bg_url = static(f'images/{filename}')
    return render(request, 'theme_list.html', {'themes': themes})


# 🆕 2. List all programs inside a theme
@login_required
def programs_by_theme(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    programs = theme.programs.all()

    for program in programs:
        # For student
        if request.user.role == 'student':
            program.is_registered = ProgramRegistration.objects.filter(
                student=request.user,
                program=program
            ).exists()

        # For teacher
        elif request.user.role == 'teacher':
            program.has_requested_to_teach = TeachingRequest.objects.filter(
                teacher=request.user,
                program=program
            ).exists()

            program.is_approved_to_teach = TeachingRequest.objects.filter(
                teacher=request.user,
                program=program,
                is_approved=True
            ).exists()

            program.has_edit_approval = EditRequest.objects.filter(
                teacher=request.user,
                program=program,
                is_approved=True
            ).exists()

    # 🆕 Check if teacher has request/approval to create programs
    program_creation_request = None
    if request.user.role == 'teacher':
        program_creation_request = ProgramCreationRequest.objects.filter(teacher=request.user).first()

    return render(request, 'programs_by_theme.html', {
        'theme': theme,
        'programs': programs,
        'program_creation_request': program_creation_request,
    })

@login_required
def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)
    activities = program.activities.all()
    guided_activity = GuidedActivity.objects.filter(program=program).first()

    is_registered = False
    is_approved = False
    registration = None

    if request.user.role == 'student':
        registration = ProgramRegistration.objects.filter(student=request.user, program=program).first()
        if registration:
            is_registered = True
            is_approved = registration.is_approved

    has_requested_to_teach = TeachingRequest.objects.filter(teacher=request.user, program=program).exists()
    is_approved_to_teach = TeachingRequest.objects.filter(teacher=request.user, program=program, is_approved=True).exists()
    has_edit_approval = EditRequest.objects.filter(program=program, teacher=request.user, is_approved=True).exists()

    approved_request = TeachingRequest.objects.filter(
        teacher=request.user,
        program=program,
        is_approved=True
    ).first()

    student_points = []
    if request.user.is_superuser or is_approved_to_teach:
        registrations = ProgramRegistration.objects.filter(
            program=program, is_approved=True
        ).select_related('student')

        for reg in registrations:
            program_points = Points.objects.filter(
                user=reg.student, program=program
            ).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

            total_points = Points.objects.filter(
                user=reg.student
            ).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

            student_points.append({
                'student': reg.student,
                'program_points': program_points,
                'total_points': total_points
            })

    can_review = request.user.is_superuser or TeachingRequest.objects.filter(
        teacher=request.user,
        program=program,
        is_approved=True
    ).exists()

    guided_activities = program.guided_activities.all()
    activities_with_deadlines = []

    for activity in guided_activities:
        timeline = ActivityTimeline.objects.filter(activity=activity, teacher__teaching_requests__program=program, teacher__teaching_requests__is_approved=True).first()
        activities_with_deadlines.append({
            'activity': activity,
            'timeline': timeline,
            'is_past_deadline': timeline.end_date < timezone.now().date() if timeline and timeline.end_date else False
        })

    context = {
        'program': program,
        'activities': activities,
        'guided_activity': guided_activity,
        'is_registered': is_registered,
        'is_approved': is_approved,
        'has_requested_to_teach': has_requested_to_teach,
        'is_approved_to_teach': is_approved_to_teach,
        'has_edit_approval': has_edit_approval,
        'approved_request': approved_request,
        'student_points': student_points, 
        'can_review': can_review,
        'activities_with_deadlines': activities_with_deadlines,

    }
    return render(request, 'program_detail.html', context)




# 🆕 4. Register student for program
@login_required
def register_program(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if request.user.role != 'student':
        messages.error(request, "Only students can register for programs.")
        return redirect('programs:program_detail', pk=pk)

    registration, created = ProgramRegistration.objects.get_or_create(
        student=request.user,
        program=program,
        defaults={
            'start_date': now(),
            'end_date': now() + timedelta(days=30),
        }
    )

    if created:
        messages.success(request, "You have registered! Pending approval.")
    else:
        messages.info(request, "You are already registered for this program.")

    return redirect('programs:program_detail', pk=pk)


# 🆕 5. Teacher request to teach a program
@login_required
def request_to_teach(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can request to teach programs.")
        return redirect('programs:program_detail', pk=pk)

    existing = TeachingRequest.objects.filter(teacher=request.user, program=program).first()

    if existing:
        messages.info(request, "You've already submitted a request to teach this program.")
    else:
        TeachingRequest.objects.create(
            teacher=request.user,
            program=program,
            start_date=now(),
            end_date=now() + timedelta(days=30),
        )
        messages.success(request, "Your request to teach this program has been submitted!")

    return redirect('programs:program_detail', pk=pk)



@login_required
def ysa_way_test_view(request):
    """Page where students take the YSA Way Test."""
    return render(request, 'ysa_way_test.html')


# 🆕 Admin Approval Views

@login_required
def approve_registration(request, registration_id):
    if not request.user.is_staff:
        messages.error(request, "Only admins can approve registrations.")
        return redirect('programs:programs')

    registration = get_object_or_404(ProgramRegistration, id=registration_id)
    registration.is_approved = True
    registration.save()
    messages.success(request, f"{registration.student.username}'s registration for {registration.program.name} has been approved!")
    return redirect('programs:program_detail', pk=registration.program.id)

@login_required
def approve_teaching_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, "Only admins can approve teaching requests.")
        return redirect('programs:programs')

    teaching_request = get_object_or_404(TeachingRequest, id=request_id)

    if teaching_request.has_completed is False:
        teaching_request.has_completed = True
        teaching_request.save()

        Points.objects.create(
            user=teaching_request.teacher,
            team=teaching_request.teacher.team,
            program=teaching_request.program,
            points_earned=10,
            reason="Completed teaching the program"
        )


        messages.success(request, f"{teaching_request.teacher.username}'s teaching request for {teaching_request.program.name} has been approved and points awarded!")
    else:
        messages.info(request, "This request was already approved.")

    return redirect('programs:program_detail', pk=teaching_request.program.id)


@login_required
def create_program(request):
    if request.user.is_superuser:
        can_create = True
    elif request.user.role == 'teacher':
        can_create = ProgramCreationRequest.objects.filter(teacher=request.user, is_approved=True).exists()
    else:
        can_create = False

    if not can_create:
        messages.error(request, "You are not authorized to create programs.")
        return redirect('core:home')

    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            if request.user.is_superuser:
                program.is_approved = True  # Auto-approved
            else:
                program.is_approved = False  # Teachers' programs need review
            program.save()

            # Award points for program creation
            from points.models import Points
            Points.objects.create(
                user=request.user,
                team=request.user.team,
                points_earned=20,
                reason=f"Created a new program: {program.name}",
                program=program
            )

            messages.success(request, "Program submitted successfully.")
            return redirect('programs:program_detail', pk=program.pk)
    else:
        form = ProgramForm()

    return render(request, 'create_program.html', {'form': form})




@login_required
def request_edit_access(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can request edit access.")
        return redirect('programs:program_detail', pk=pk)

    # Check if already requested
    exists = EditRequest.objects.filter(program=program, teacher=request.user).exists()
    if not exists:
        EditRequest.objects.create(program=program, teacher=request.user)
        messages.success(request, "Your request to edit this program has been submitted.")
    else:
        messages.info(request, "You have already requested to edit this program.")

    return redirect('programs:program_detail', pk=pk)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_edit_request(request, request_id):
    edit_request = get_object_or_404(EditRequest, id=request_id)
    edit_request.is_approved = True
    edit_request.save()
    messages.success(request, f"{edit_request.teacher.username} is now approved to edit {edit_request.program.name}.")
    return redirect('users:admin_dashboard')

@login_required
def add_activity(request, program_id):
    program = get_object_or_404(Program, id=program_id)

    # Access control: only admins or approved teachers
    is_teacher_approved = request.user.role == 'teacher' and program.teaching_requests.filter(
        teacher=request.user, is_approved=True
    ).exists()

    if not (request.user.is_superuser or is_teacher_approved):
        messages.error(request, "You don't have permission to add activities.")
        return redirect('programs:program_detail', pk=program_id)

    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.program = program
            activity.save()
            messages.success(request, "Activity added successfully.")
            return redirect('programs:program_detail', pk=program_id)
    else:
        form = ActivityForm()

    return render(request, 'add_activity.html', {'form': form, 'program': program})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'teacher')
def create_guided_activity(request, program_id):
    program = get_object_or_404(Program, pk=program_id)

    if not (request.user.is_superuser or request.user.role == 'teacher'):
        messages.error(request, "You don't have permission to add a guided activity.")
        return redirect('programs:program_detail', program_id)

    if request.method == 'POST':
        form = GuidedActivityForm(request.POST)
        if form.is_valid():
            guided_activity = form.save(commit=False)
            guided_activity.program = program
            guided_activity.save()
            messages.success(request, "Guided activity created successfully.")
            return redirect('programs:add_steps', guided_activity.id)
    else:
        form = GuidedActivityForm()

    return render(request, 'create_guided_activity.html', {'form': form, 'program': program})


# Step 2: Student View of GuidedActivity Steps
@login_required
@user_passes_test(lambda u: u.role == 'student')
def complete_step(request, step_id):
    step = get_object_or_404(ActivityStep, id=step_id)
    program = step.activity.program
    # Ensure student is registered
    if not program.registrations.filter(student=request.user, is_approved=True).exists():
        return redirect('programs:program_detail', pk=program.id)

    response, created = StepResponse.objects.get_or_create(step=step, student=request.user)
    if request.method == 'POST':
        response.response = request.POST.get('response')
        response.save()
        next_step = step.activity.steps.filter(order__gt=step.order).first()
        if next_step:
            return redirect('programs:complete_step', step_id=next_step.id)
        return redirect('programs:program_detail', pk=program.id)

    return render(request, 'complete_step.html', {
        'step': step,
        'response': response,
    })



@login_required
def add_steps(request, activity_id):
    activity = get_object_or_404(GuidedActivity, pk=activity_id)

    StepFormSet = modelformset_factory(
        ActivityStep,
        form=ActivityStepForm,
        extra=14,
        can_delete=True
    )

    queryset = ActivityStep.objects.filter(activity=activity)

    if request.method == 'POST':
        formset = StepFormSet(request.POST, request.FILES, queryset=queryset)

        if formset.is_valid():
            steps = formset.save(commit=False)

            # Set FK and save only once per step
            for step in steps:
                step.activity = activity
                step.save()

            # Delete removed steps
            for obj in formset.deleted_objects:
                obj.delete()

            # Optional: only if you're using m2m fields in your form
            # formset.save_m2m()

            messages.success(request, "Steps saved successfully.")
            return redirect('programs:program_detail', pk=activity.program.id)
        else:
            for i, form in enumerate(formset.forms):
                print(f"Form {i} errors: {form.errors}")

            messages.error(request, "There was a problem saving your steps. Please check the form.")
    else:
        formset = StepFormSet(queryset=queryset)

    return render(request, 'add_steps.html', {
        'formset': formset,
        'activity': activity,
    })


@login_required
def submit_step_response(request, step_id):
    step = get_object_or_404(ActivityStep, id=step_id)
    response = StepResponse.objects.filter(step=step, student=request.user).first()

    if request.method == 'POST':
        if not response:
            response = StepResponse(step=step, student=request.user)

        # Handle multiple choice (checkboxes or radio)
        if step.step_type == "multiple_choice":
            answers = request.POST.getlist('response')
            response.response = ", ".join(answers)
        else:
            response.response = request.POST.get('response', '')

        if step.step_type == "video" and 'video' in request.FILES:
            response.video = request.FILES['video']

        response.save()

        timeline = ActivityTimeline.objects.filter(activity=step.activity, teacher__in=[request.user, request.user.assigned_teacher if hasattr(request.user, 'assigned_teacher') else None]).first()

        if timeline and timeline.end_date and timezone.now().date() > timeline.end_date:
            messages.warning(request, "Note: You submitted this step after the deadline.")


        # ✅ Award points if not already awarded for this step
        already_awarded = Points.objects.filter(
            user=request.user,
            step=step,
            program=step.activity.program,
        ).exists()

        if not already_awarded and step.points > 0:
            Points.objects.create(
                user=request.user,
                step=step,
                program=step.activity.program,
                points_earned=step.points,
                reason=f"Completed step {step.step_key} of {step.activity.title}"
            )

        messages.success(request, "Response submitted.")

        # Next step
        next_step = step.activity.steps.filter(order__gt=step.order).first()
        if next_step:
            return redirect('programs:complete_step', step_id=next_step.id)
        return redirect('programs:program_detail', pk=step.activity.program.id)

    # Multiple-choice mode (radio vs checkbox)
    multiple_correct = step.options.filter(is_correct=True).count() > 1

    return render(request, 'complete_step.html', {
        'step': step,
        'response': response or StepResponse(step=step, student=request.user),
        'multiple_correct': multiple_correct,
    })



@login_required
def view_guided_activity(request, activity_id):
    activity = get_object_or_404(GuidedActivity, pk=activity_id)
    steps = list(activity.steps.all().order_by('order'))

    # ⛔️ Only block students (not teachers/admins)
    if request.user.role == 'student':
        # Check timeline for this student
        program = activity.program
        registration = ProgramRegistration.objects.filter(program=program, student=request.user, is_approved=True).first()
        if registration:
            # Get the activity timeline
            timeline = ActivityTimeline.objects.filter(activity=activity).first()
            if timeline and timeline.end_date and timeline.end_date < date.today():
                messages.error(request, "This activity is no longer accessible. The deadline has passed.")
                return redirect('programs:program_detail', pk=program.id)

    # Continue as normal
    responses = StepResponse.objects.filter(student=request.user, step__in=steps)
    completed_step_ids = {r.step_id for r in responses}

    unlocked_step_ids = set()
    for i, step in enumerate(steps):
        if i == 0 or steps[i - 1].id in completed_step_ids:
            unlocked_step_ids.add(step.id)

    # Optional: get timeline to display
    timeline = ActivityTimeline.objects.filter(activity=activity).first()

    return render(request, 'view_guided_activity.html', {
        'activity': activity,
        'steps': steps,
        'responses': completed_step_ids,
        'unlocked_steps': unlocked_step_ids,
        'timeline': timeline,  # For UI display
    })



@login_required
def review_guided_activity(request, activity_id):
    activity = get_object_or_404(GuidedActivity, id=activity_id)
    program = activity.program

    # Permissions
    can_assign_timeline = False
    if not request.user.is_superuser:
        is_teacher = TeachingRequest.objects.filter(
            teacher=request.user, program=program, is_approved=True
        ).exists()
        if not is_teacher:
            messages.error(request, "Access denied.")
            return redirect('core:home')
        can_assign_timeline = True
    else:
        can_assign_timeline = True  # superusers can always assign

    # Fetch the current teacher's timeline (if exists)
    teacher_timeline = None
    if request.user.role == 'teacher' or request.user.is_superuser:
        teacher_timeline = activity.timelines.filter(teacher=request.user).first()

    steps = activity.steps.all().order_by('order')
    responses_by_step = {}

    for step in steps:
        responses = StepResponse.objects.filter(step=step).select_related('student')
        for response in responses:
            point = Points.objects.filter(user=response.student, step=step).first()
            response.awarded_points = point.points_earned if point else None
        responses_by_step[step] = responses

    return render(request, 'review_guided_activity.html', {
        'activity': activity,
        'steps': steps,
        'responses_by_step': responses_by_step,
        'can_assign_timeline': can_assign_timeline,
        'teacher_timeline': teacher_timeline,  # 👈 Add this to show timeline in template
    })



@login_required
def assign_step_points(request, step_id, student_id):
    step = get_object_or_404(ActivityStep, id=step_id)
    student = get_object_or_404(CustomUser, id=student_id)

    if request.method == 'POST':
        try:
            additional_points = int(request.POST.get('points', 0))
        except ValueError:
            messages.error(request, "Invalid point value.")
            return redirect('programs:review_guided_activity', activity_id=step.activity.id)

        program = step.activity.program
        team = getattr(student, 'team', None)

        # Get or create the Points object
        points_obj, created = Points.objects.get_or_create(
            user=student,
            step=step,
            defaults={
                'points_earned': 0,
                'program': program,
                'team': team,
                'reason': f"Manual grading for step {step.step_key}",
            }
        )

        # Add new points to existing
        points_obj.points_earned += additional_points
        points_obj.program = program  # ensure updated if needed
        points_obj.team = team
        points_obj.reason = f"Manual grading for step {step.step_key}"
        points_obj.save()

        messages.success(request, f"Awarded {additional_points} more point(s) to {student.get_full_name()}. Total: {points_obj.points_earned}")
        return redirect('programs:review_guided_activity', activity_id=step.activity.id)





@login_required
def edit_program(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if request.user.is_superuser:
        has_permission = True
    else:
        has_teach_approval = TeachingRequest.objects.filter(
            program=program, teacher=request.user, is_approved=True
        ).exists()
        has_edit_approval = EditRequest.objects.filter(
            program=program, teacher=request.user, is_approved=True
        ).exists()
        has_permission = has_teach_approval and has_edit_approval

    if not has_permission:
        messages.error(request, "You are not authorized to edit this program yet.")
        return redirect('programs:program_detail', pk=pk)

    program_form = ProgramForm(request.POST or None, instance=program)

    investigation_form = None
    if request.user.is_superuser:
        investigation, _ = InvestigationProcedure.objects.get_or_create(program=program)
        investigation_form = InvestigationProcedureForm(request.POST or None, request.FILES or None, instance=investigation)

    if request.method == 'POST':
        if program_form.is_valid():
            program_form.save()
            if investigation_form and investigation_form.is_valid():
                investigation_form.save()
            messages.success(request, "Program updated successfully.")
            return redirect('programs:program_detail', pk=pk)

    return render(request, 'edit_program.html', {
        'form': program_form,
        'program': program,
        'investigation_form': investigation_form,
    })


@login_required
def mark_teaching_completed(request, request_id):
    teaching_request = get_object_or_404(TeachingRequest, id=request_id, teacher=request.user)

    if request.method == 'POST' and teaching_request.is_approved and not teaching_request.has_completed:
        teaching_request.has_completed = True
        teaching_request.completed_at = now()
        teaching_request.save()

        # Award points
        Points.objects.create(
            user=request.user,
            team=request.user.team,
            points_earned=10,
            reason=f"Finished teaching {teaching_request.program.name}",
            program=teaching_request.program
        )

        messages.success(request, "🎉 You’ve marked the program as completed and earned 25 points!")
    return redirect('programs:program_detail', pk=teaching_request.program.id)


@login_required
def request_program_creation(request):
    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can request to create programs.")
        return redirect('core:home')

    exists = ProgramCreationRequest.objects.filter(teacher=request.user).first()
    if exists:
        messages.info(request, "You have already submitted a request.")
    else:
        ProgramCreationRequest.objects.create(teacher=request.user)
        messages.success(request, "Your request to create programs has been submitted!")
    theme = Theme.objects.first()
    return redirect('programs:programs_by_theme', theme_id=theme.id)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_program_creation(request, request_id):
    creation_request = get_object_or_404(ProgramCreationRequest, id=request_id)
    if request.method == "POST":
        creation_request.is_approved = True
        creation_request.save()
        messages.success(request, f"Program creation request '{creation_request.title}' has been approved.")
    return redirect('users:admin_dashboard')


@login_required
def assign_activity_timeline(request, activity_id):
    activity = get_object_or_404(GuidedActivity, id=activity_id)

    if not request.user.is_superuser and not request.user.role == 'teacher':
        return HttpResponseForbidden("Not authorized.")

    form = ActivityTimelineForm(request.POST or None)

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # 🔁 Create or update the existing timeline
        timeline, created = ActivityTimeline.objects.update_or_create(
            activity=activity,
            teacher=request.user,
            defaults={'start_date': start_date, 'end_date': end_date}
        )

        messages.success(request, "Timeline successfully assigned.")
        return redirect('programs:review_guided_activity', activity_id=activity.id)

    return render(request, 'assign_timeline.html', {
        'form': form,
        'activity': activity,
    })

