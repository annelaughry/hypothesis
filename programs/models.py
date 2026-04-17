from django.db import models
from django.conf import settings
from users.models import CustomUser
from django.utils import timezone
from django.utils.text import slugify


class Goal(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='goal_tiles/')
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Theme(models.Model):
    name = models.CharField(max_length=100)
    is_locked = models.BooleanField(default=True)
    background_image = models.ImageField(upload_to='themes/backgrounds/', blank=True, null=True)

    def __str__(self):
        return self.name

    def is_locked_for_user(self, user):
        if user.is_superuser or user.role == 'teacher':
            return False
        if hasattr(user, 'ysawaytest'):
            return not user.ysawaytest.has_passed
        return True


class Program(models.Model):
    goal = models.ForeignKey('Goal', on_delete=models.CASCADE, related_name='programs', null=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=255)
    description = models.TextField()
    overview = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    difficulty_level = models.CharField(
        max_length=50,
        choices=[('Explorer', 'Explorer'), ('Ambassador', 'Ambassador')],
        default='Explorer'
    )
    materials = models.TextField(blank=True)
    estimated_time = models.CharField(max_length=100, blank=True)
    keywords = models.TextField(blank=True)
    us_standards = models.TextField(blank=True)
    moldovan_standards = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
 #-------------------------------------------------------------   
#Datasets model:

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal = models.ForeignKey(Goal, related_name='datasets', on_delete=models.CASCADE)
    uploaded_csv = models.FileField(upload_to='datasets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class DataRow(models.Model):
    dataset = models.ForeignKey(Dataset, related_name='rows', on_delete=models.CASCADE)
    data = models.JSONField()  # stores each row as {col1: value, col2: value}

    def __str__(self):
        return f"Row {self.id} of {self.dataset.name}"
    
#-------------------------------------------------------------------

class InvestigationProcedure(models.Model):
    program = models.OneToOneField(Program, on_delete=models.CASCADE, related_name='investigation')

    pre_lab = models.TextField(blank=True)
    pre_lab_link = models.URLField(blank=True, null=True)
    pre_lab_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    observation = models.TextField(blank=True)
    observation_link = models.URLField(blank=True, null=True)
    observation_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    idea = models.TextField(blank=True)
    idea_link = models.URLField(blank=True, null=True)
    idea_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    hypothesis = models.TextField(blank=True)
    hypothesis_link = models.URLField(blank=True, null=True)
    hypothesis_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    experiment = models.TextField(blank=True)
    experiment_link = models.URLField(blank=True, null=True)
    experiment_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    analysis = models.TextField(blank=True)
    analysis_link = models.URLField(blank=True, null=True)
    analysis_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    communication = models.TextField(blank=True)
    communication_link = models.URLField(blank=True, null=True)
    communication_file = models.FileField(upload_to='investigation_files/', blank=True, null=True)

    def __str__(self):
        return f"Investigation for {self.program.name}"

# --------------------
# Activities (simple + guided)
# --------------------

class Activity(models.Model):
    program = models.ForeignKey(Program, related_name='activities', on_delete=models.CASCADE, null = True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    resource_file = models.FileField(upload_to='activity_files/', blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.program.name} - {self.title}"


class GuidedActivity(models.Model):
    program = models.ForeignKey(Program, related_name='guided_activities', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # ✔️ Required by default
    overview = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.program.name} - {self.title}"



class ActivityStep(models.Model):
    STEP_CHOICES = [
        ('pre_lab', 'Pre-Lab Activity'),
        ('observation', 'Observation'),
        ('idea', 'Idea'),
        ('hypothesis', 'Hypothesis'),
        ('experiment', 'Experiment'),
        ('results_analysis', 'Results and Analysis'),
        ('communication', 'Communication'),
    ]

    STEP_TYPE_CHOICES = [
        ('short_answer', 'Short Answer'),
        ('long_answer', 'Long Answer'),
        ('fill_blank', 'Fill in the Blank'),
        ('multiple_choice', 'Multiple Choice'),
        ('video', 'Video Response'),
    ]

    activity = models.ForeignKey(GuidedActivity, related_name='steps', on_delete=models.CASCADE)
    step_key = models.CharField(max_length=30, choices=STEP_CHOICES)
    instructions = models.TextField()
    step_type = models.CharField(max_length=30, choices=STEP_TYPE_CHOICES, default='short_answer')
    points = models.PositiveIntegerField(default=0)
    question = models.TextField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    attached_file = models.FileField(upload_to='activity_files/', blank=True, null=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_step_key_display()} ({self.step_type})"


class StepOption(models.Model):
    step = models.ForeignKey(ActivityStep, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    blank_placeholder = models.BooleanField(default=False)  # for fill-in-the-blank alignment

    def __str__(self):
        return self.text


class StepResponse(models.Model):
    step = models.ForeignKey(ActivityStep, related_name='responses', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    response = models.TextField(blank=True)
    video = models.FileField(upload_to='step_videos/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('step', 'student')

    def __str__(self):
        return f"{self.student.username} - Step {self.step.order} ({self.step.activity.title})"

# --------------------
# User Access & Requests
# --------------------

class ProgramRegistration(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name="program_registrations"
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="registrations")
    is_approved = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} -> {self.program.name}"


class TeachingRequest(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name="teaching_requests"
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="teaching_requests")
    is_approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    has_completed = models.BooleanField(default=False) 
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"{self.teacher.username} wants to teach {self.program.name}"


class EditRequest(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.username} requests edit for {self.program.name}"


class YSAWayTest(models.Model):
    teacher = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    has_passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.username} - {'Passed' if self.has_passed else 'Not Passed'}"    


class ProgramCreationRequest(models.Model):
    teacher = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.teacher}"
    

class ActivityTimeline(models.Model):
    activity = models.ForeignKey('GuidedActivity', on_delete=models.CASCADE, related_name='timelines')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('activity', 'teacher')

    def __str__(self):
        return f"{self.activity.title} Timeline by {self.teacher.username}"

