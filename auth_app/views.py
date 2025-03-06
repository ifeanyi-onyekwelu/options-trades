from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from .decorators import guest_only
from django.contrib import messages
from users.models import User
from django.views.generic import FormView
from django.contrib.auth import login
from .forms import SignupForm, LoginForm

@method_decorator(guest_only, name="dispatch")
class CustomLoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy("user:dashboard")

    def dispatch(self, request, *args, **kwargs):
        print("Dispatch method called")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        print("GET method called")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("POST method called")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        print("get_success_url called")
        user = self.request.user
        if user.is_superuser or user.is_staff:
            print("Redirecting to admin dashboard")
            return reverse_lazy("admin:dashboard")
        print("Redirecting to user dashboard")
        return reverse_lazy("user:dashboard")

    def form_valid(self, form):
        print("form_valid called")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        
        print(f"Form valid - Email: {email}, Password: {password}")

        user = User.objects.filter(email=email).first()
        if user:
            print(f"User found: {user}")
        else:
            print("User not found")

        if user and user.check_password(password):
            print("Password correct - logging in user")
            login(self.request, user)
            return super().form_valid(form)

        print("Invalid email or password")
        messages.error(self.request, "Invalid email or password")
        return self.form_invalid(form)

    def form_invalid(self, form):
        print("form_invalid called")
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)


class SignupView(FormView):
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("user:dashboard")

    def form_valid(self, form):
        user = form.save()  # The form handles saving
        login(self.request, user)

        messages.success(self.request, "Registration successful")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was a problem with your registration.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ref"] = self.request.GET.get("ref")
        return context


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("auth:login")
