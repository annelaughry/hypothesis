from django import forms
from .models import FoodEntry, Dish

class FoodEntryForm(forms.ModelForm):
    new_dish = forms.CharField(
        required=False,
        label="New Dish (if not listed)",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a dish not in the list',
            'class': 'form-control'
        })
    )

    class Meta:
        model = FoodEntry
        fields = ['dishes', 'new_dish', 'waste_reason', 'comments']
        widgets = {
            'dishes': forms.CheckboxSelectMultiple(),
            'waste_reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Why was food wasted (if applicable)?',
                'class': 'form-control'
            }),
            'comments': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any other comments?',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dishes'].queryset = Dish.objects.order_by('name')

