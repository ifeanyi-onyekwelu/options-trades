from django import forms
from app.models import InvestmentPlan
from users.models import User


class InvestmentPlanForm(forms.ModelForm):
    class Meta:
        model = InvestmentPlan
        fields = [
            "name",
            "starting_price",
            "maximum_price",
            "returns_percentage",
            "duration_days",
            "total_returns_percentage",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "starting_price": forms.NumberInput(attrs={"class": "form-control"}),
            "maximum_price": forms.NumberInput(attrs={"class": "form-control"}),
            "returns_percentage": forms.NumberInput(attrs={"class": "form-control"}),
            "duration_days": forms.NumberInput(attrs={"class": "form-control"}),
            "total_returns_percentage": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }


class AdminEmailForm(forms.Form):
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email Subject"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Email Message"}
        )
    )
    recipient = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = User.objects.filter(is_superuser=False, is_staff=False)
        user_choices = [(user.email, user.email) for user in users]
        user_choices.insert(0, ("all", "All Users"))  # Option to send to all
        self.fields["recipient"].choices = user_choices


class AddRemoveFundsForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    action = forms.ChoiceField(
        choices=[("add", "Add Funds"), ("remove", "Remove Funds")]
    )
