from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import (
    Program, Activity, ProgramRegistration, TeachingRequest, YSAWayTest,
    GuidedActivity, ActivityStep, StepResponse, StepOption, InvestigationProcedure,
    ActivityTimeline, Dataset, DataRow
)


# ----------------------------
# Program & Activity Forms
# ----------------------------

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            'theme', 'name', 'description', 'overview', 'objective',
            'difficulty_level', 'materials', 'estimated_time', 'keywords',
            'us_standards', 'moldovan_standards'
        ]
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'overview': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'difficulty_level': forms.Select(attrs={'class': 'form-control'}),
            'materials': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estimated_time': forms.TextInput(attrs={'class': 'form-control'}),
            'keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'us_standards': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'moldovan_standards': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['program', 'title', 'description', 'instructions', 'points', 'resource_file', 'external_link']
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'resource_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control'}),
        }


# ----------------------------
# User Interaction Forms
# ----------------------------

class ProgramRegistrationForm(forms.ModelForm):
    class Meta:
        model = ProgramRegistration
        fields = ['student', 'program', 'is_approved', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TeachingRequestForm(forms.ModelForm):
    class Meta:
        model = TeachingRequest
        fields = ['program', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class YSAWayTestForm(forms.ModelForm):
    class Meta:
        model = YSAWayTest
        fields = []


# ----------------------------
# Guided Activity Forms
# ----------------------------

class GuidedActivityForm(forms.ModelForm):
    class Meta:
        model = GuidedActivity
        fields = ['title', 'overview']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'overview': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),  # no 'required'
        }


class ActivityStepForm(forms.ModelForm):
    class Meta:
        model = ActivityStep
        fields = [
            'step_key', 'question', 'step_type', 'points',
            'external_link', 'order', 'attached_file'
        ]
        widgets = {
            'step_key': forms.Select(attrs={'class': 'form-control'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'step_type': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'attached_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



class StepResponseForm(forms.ModelForm):
    class Meta:
        model = StepResponse
        fields = ['response', 'video']
        widgets = {
            'response': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ActivityTimelineForm(forms.ModelForm):
    class Meta:
        model = ActivityTimeline
        fields = ['activity', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


# ----------------------------
# Step Option Form & FormSet
# ----------------------------

class StepOptionForm(forms.ModelForm):
    class Meta:
        model = StepOption
        fields = ['text', 'is_correct', 'blank_placeholder']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'blank_placeholder': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


StepOptionFormSet = inlineformset_factory(
    ActivityStep,
    StepOption,
    form=StepOptionForm,
    extra=4,
    can_delete=True
)


# ----------------------------
# Investigation Form
# ----------------------------

class InvestigationProcedureForm(forms.ModelForm):
    class Meta:
        model = InvestigationProcedure
        fields = '__all__'


# ----------------------------
# Datasets Form
# ----------------------------

class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'goal', 'uploaded_csv']


class DataRowForm(forms.ModelForm):
    class Meta:
        model = DataRow
        fields = ['data']  # JSON field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget = forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter as JSON, e.g., {"col1": "value1", "col2": "value2"}'})
