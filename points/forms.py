from django import forms
from .models import Points
from programs.models import Program

class AddPointsForm(forms.ModelForm):
    class Meta:
        model = Points
        fields = ['points_earned', 'reason', 'program']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_superuser:
                self.fields['program'].queryset = Program.objects.all()
            elif user.role == 'teacher':
                self.fields['program'].queryset = Program.objects.filter(
                    teaching_requests__teacher=user,
                    teaching_requests__is_approved=True
                )


class DeductPointsForm(forms.ModelForm):
    class Meta:
        model = Points
        fields = ['points_earned', 'reason', 'program']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                self.fields['program'].queryset = Program.objects.all()
            elif user.role == 'teacher':
                self.fields['program'].queryset = Program.objects.filter(
                    teaching_requests__teacher=user,
                    teaching_requests__is_approved=True
                )

        self.fields['points_earned'].label = "Points to Deduct"
        self.fields['points_earned'].help_text = "Enter a positive number (it will be deducted automatically)."

    def clean_points_earned(self):
        value = self.cleaned_data['points_earned']
        return -abs(value)
