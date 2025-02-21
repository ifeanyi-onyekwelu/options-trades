from django import forms
from app.models import InvestmentPlan

class InvestmentPlanForm(forms.ModelForm):
    class Meta:
        model = InvestmentPlan
        fields = ['name', 'starting_price', 'maximum_price', 'returns_percentage', 'duration_days', 'total_returns_percentage']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'returns_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_returns_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }
