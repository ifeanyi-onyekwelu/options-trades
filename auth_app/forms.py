from django import forms
from users.models import User
from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Email",
                "required": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password",
                "required": True,
                "id": "password",
            }
        )
    )


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password",
                "id": "password1",
            }
        ),
        label="Password",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Confirm Password",
                "id": "password2",
            }
        ),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "First name",
                    "id": "fname",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Last name",
                    "id": "lname",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Email",
                    "id": "email",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user
