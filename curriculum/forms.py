from django import forms
from django.forms import inlineformset_factory
from .models import GuidedResearchActivity, ResearchMaterial, ResearchStandard, ActivityFile, Standard


class GuidedResearchActivityForm(forms.ModelForm):
    standards = forms.ModelMultipleChoiceField(
        queryset=Standard.objects.filter(active=True).order_by("framework", "code"),
        required=False,
        label="Standards",
    )

    class Meta:
        model = GuidedResearchActivity
        fields = [
            "title",
            "overview",
            "standards",
            "objectives",
            "keywords",
            "observation",
            "question",
            "hypothesis",
            "test",
            "analysis",
            "communication",
        ]


MaterialFormSet = inlineformset_factory(
    GuidedResearchActivity,
    ResearchMaterial,
    fields=["text"],
    extra=0,
    can_delete=True
)

StandardFormSet = inlineformset_factory(
    GuidedResearchActivity,
    ResearchStandard,
    fields=["text"],
    extra=0,
    can_delete=True
)

FileFormSet = inlineformset_factory(
    GuidedResearchActivity,
    ActivityFile,
    fields=["file", "description"],
    extra=0,  # start with 0, we add via JS
    can_delete=True,
)
