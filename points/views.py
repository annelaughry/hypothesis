from django.shortcuts import render, get_object_or_404, redirect
from .serializers import PointsSerializer
from .models import Points 
from programs.models import Program
from rest_framework.views import APIView
from rest_framework.response import Response
from points.utils import LEVELS
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from django.db.models import Sum
from programs.models import TeachingRequest, ProgramRegistration, StepResponse, Program
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AddPointsForm, DeductPointsForm
from django.contrib import messages



# Points API View
class PointsAPIView(APIView):
    def get(self, request):
        points = Points.objects.all()
        serializer = PointsSerializer(points, many=True)
        return Response(serializer.data)

@login_required
def level_detail(request):
    return render(request, 'level_detail.html', {
        'levels': LEVELS
    })


@login_required
def manage_points_view(request):
    user = request.user

    # Get filter (program ID from dropdown)
    selected_program_id = request.GET.get("program")
    selected_program = None

    if user.is_superuser:
        students = CustomUser.objects.filter(role='student')
        programs = Program.objects.all()
    elif user.role == 'teacher':
        programs = Program.objects.filter(
            teaching_requests__teacher=user,
            teaching_requests__is_approved=True
        )
        approved_programs = programs
        students = CustomUser.objects.filter(
            program_registrations__program__in=approved_programs,
            program_registrations__is_approved=True
        ).distinct()
    else:
        return redirect('core:home')

    # Apply selected program filter if any
    if selected_program_id:
        try:
            selected_program = Program.objects.get(id=selected_program_id)
        except Program.DoesNotExist:
            selected_program = None

    # Compile points summary
    student_points = []
    for student in students:
        total_points = Points.objects.filter(user=student).aggregate(
            total=Sum('points_earned')
        )['total'] or 0

        program_points = 0
        if selected_program:
            program_points = Points.objects.filter(
                user=student,
                program=selected_program
            ).aggregate(total=Sum('points_earned'))['total'] or 0

        student_points.append({
            'student': student,
            'total_points': total_points,
            'program_points': program_points
        })

    return render(request, 'manage_points.html', {
        'student_points': student_points,
        'programs': programs,
        'selected_program': selected_program,
        'is_admin': user.is_superuser,
    })


@login_required
def add_points_view(request, user_id):
    student = get_object_or_404(CustomUser, id=user_id, role='student')

    # Check permission
    if request.user.is_superuser:
        pass
    elif request.user.role == 'teacher':
        approved_programs = Program.objects.filter(
            teaching_requests__teacher=request.user,
            teaching_requests__is_approved=True
        )
        is_allowed = ProgramRegistration.objects.filter(
            student=student,
            program__in=approved_programs,
            is_approved=True
        ).exists()
        if not is_allowed:
            messages.error(request, "You can only award points to your own students.")
            return redirect('points:manage_points')
    else:
        return redirect('core:home')

    if request.method == "POST":
        form = AddPointsForm(request.POST or None, user=request.user)
        if form.is_valid():
            point = form.save(commit=False)
            point.user = student
            point.team = student.team
            point.program = form.cleaned_data.get("program")
            point.save()

            # ✅ Update profile total
            if hasattr(student, 'profile'):
                student.profile.update_points()

            messages.success(request, f"{point.points_earned} points added to {student.get_full_name()}.")
            return redirect('points:manage_points')
    else:
        form = AddPointsForm(user=request.user)

    return render(request, 'add_points.html', {
        'form': form,
        'student': student
    })


@login_required
def deduct_points_view(request, user_id):
    student = get_object_or_404(CustomUser, id=user_id, role='student')

    # Access control
    if request.user.is_superuser:
        pass
    elif request.user.role == 'teacher':
        approved_programs = Program.objects.filter(
            teaching_requests__teacher=request.user,
            teaching_requests__is_approved=True
        )
        is_allowed = ProgramRegistration.objects.filter(
            student=student,
            program__in=approved_programs,
            is_approved=True
        ).exists()
        if not is_allowed:
            messages.error(request, "You can only deduct points from your own students.")
            return redirect('points:manage_points')
    else:
        return redirect('core:home')

    # Form submission
    if request.method == "POST":
        form = DeductPointsForm(request.POST or None, user=request.user)
        if form.is_valid():
            point = form.save(commit=False)
            point.user = student
            point.team = student.team
            point.program = form.cleaned_data.get("program")
            point.save()

            # ✅ Update student profile points total
            if hasattr(student, 'profile'):
                student.profile.update_points()

            messages.success(request, f"{abs(point.points_earned)} points deducted from {student.get_full_name()}.")
            return redirect('points:manage_points')
    else:
        form = DeductPointsForm(user=request.user)

    return render(request, 'deduct_points.html', {
        'form': form,
        'student': student
    })

