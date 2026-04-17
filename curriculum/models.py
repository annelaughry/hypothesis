from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings

class Theme(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GuidedResearchActivity(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='guided_activities')
    title = models.CharField(max_length=200)
    overview = models.TextField(blank=True)
    standards = models.ManyToManyField(
        "curriculum.Standard",
        related_name="activities",
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guided_activities_created'
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    objectives = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    observation = models.TextField(blank=True)
    question = models.TextField(blank=True)
    hypothesis = models.TextField(blank=True)
    test = models.TextField(blank=True)
    analysis = models.TextField(blank=True)
    communication = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guided_activities_created'
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('curriculum:activity_detail', args=[self.pk])



class BackgroundResearchLink(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='background_links')
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.theme.name})"


class ProjectGuide(models.Model):
    theme = models.OneToOneField(Theme, on_delete=models.CASCADE, related_name='project_guide')
    title = models.CharField(max_length=200)
    overview = models.TextField(blank=True)
    document_url = models.URLField(blank=True)   # or swap for FileField later
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.theme.name})"
    
class ResearchStandard(models.Model):
    activity = models.ForeignKey(
        GuidedResearchActivity,
        on_delete=models.CASCADE,
        related_name='standards_list'
    )
    text = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.text or "(empty)"


class ResearchMaterial(models.Model):
    activity = models.ForeignKey(
        GuidedResearchActivity,
        on_delete=models.CASCADE,
        related_name='materials_list'
    )
    text = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.text or "(empty)"
    
class ActivityFile(models.Model):
    activity = models.ForeignKey(
        GuidedResearchActivity,
        on_delete=models.CASCADE,
        related_name="files",
    )
    file = models.FileField(upload_to="activity_files/")
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description or self.file.name


#Lesson Standards 
class Standard(models.Model):
    FRAMEWORK_CHOICES = [
        ("NGSS", "NGSS"),
        ("NC", "North Carolina"),
        ("CCSS", "Common Core"),
        ("OTHER", "Other"),
    ]

    framework = models.CharField(
        max_length=20,
        choices=FRAMEWORK_CHOICES,
        default="NGSS",
    )
    code = models.CharField(max_length=50)          # e.g. MS-ESS2-4
    description = models.TextField()               # full standard text
    grade_band = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. 6–8, 9–12",
    )
    subject = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. Earth Science, Physical Science",
    )
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("framework", "code")
        ordering = ["framework", "code"]

    def __str__(self):
        return f"{self.framework} {self.code}: {self.description[:60]}..."
