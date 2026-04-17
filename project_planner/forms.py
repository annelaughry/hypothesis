from django import forms
from django.forms import inlineformset_factory
from .models import BackgroundResearch, ResearchQuestions, Hypothesis, ExperimentalDesign, GroupMember, Project

class BackgroundResearchForm(forms.ModelForm):
    class Meta:
        model = BackgroundResearch
        fields = [
            "topic",
            "big_picture",
            "prior_findings",
            "key_terms",
            "term_definitions",
            "current_events",
            "real_world",
            "sources",
        ]
        widgets = {
            "topic": forms.TextInput(attrs={"class": "form-control"}),
            "big_picture": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "prior_findings": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "key_terms": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "term1, term2, term3"}),
            "term_definitions": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "current_events": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "real_world": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "sources": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Author, Title, Year — URL"}),
        }

class ResearchQuestionsForm(forms.ModelForm):
    class Meta:
        model = ResearchQuestions
        fields = [
            "problem_statement",
            "question_brainstorm",
            "so_what",
            "evaluate",
            "final_question",
        ]
        widgets = {
            "problem_statement": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "question_brainstorm": forms.Textarea(
                attrs={"rows": 6, "class": "form-control",
                       "placeholder": "How might ...?\nWhy does ...?\nWhat causes ...?"}
            ),
            "so_what": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "evaluate": forms.Textarea(
                attrs={"rows": 3, "class": "form-control",
                       "placeholder": "List 1–2 potential questions that interest you the most and why they’re promising"}
            ),
            "final_question": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

class HypothesisForm(forms.ModelForm):
    class Meta:
        model = Hypothesis
        fields = [
            "hypothesis",
            "independent_variable",
            "dependent_variable",
        ]
        widgets = {
            "hypothesis": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "If [independent variable] changes, then [dependent variable] will ...",
                }
            ),
            "independent_variable": forms.TextInput(attrs={"class": "form-control"}),
            "dependent_variable": forms.TextInput(attrs={"class": "form-control"}),
        }

class ExperimentalDesignForm(forms.ModelForm):
    class Meta:
        model = ExperimentalDesign
        fields = [
            "materials",
            "setup_description",
            "setup_image",
            "observations",
            "data_table",
            "experiment_photos",
        ]
        widgets = {
            "materials": forms.Textarea(
                attrs={"rows": 5, "class": "form-control", "placeholder": "e.g.,\n1. 500ml Beaker\n2. Distilled water..."}
            ),
            "setup_description": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "setup_image": forms.FileInput(attrs={"class": "form-control"}),
            "observations": forms.Textarea(
                attrs={"rows": 5, "class": "form-control", "placeholder": "Notes on what happened during the test..."}
            ),
            "data_table": forms.Textarea(
                attrs={
                    "rows": 10, 
                    "class": "form-control", 
                    "placeholder": "Trial | Variable A | Result\n1 | 10 | 25\n2 | 20 | 30..."
                }
            ),
            "experiment_photos": forms.FileInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

'''ExperimentPhotoFormSet = inlineformset_factory(
    ExperimentalDesign, ExperimentPhoto, 
    fields=("image", "caption"), 
    extra=3, can_delete=True,
    widgets={
        "image": forms.FileInput(attrs={"class": "form-control"}),
        "caption": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter caption..."}),
    }
)'''

class StartProjectForm(forms.Form):
    title = forms.CharField(
        label="Project Title",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Air Quality & Asthma at Our School"}),
    )
    member_names = forms.CharField(
        label="Group Member Names",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "One name per line"}),
        help_text="Enter one name per line. Emails optional: Name <email@example.com>",
        required=False,
    )