from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .decorators import guest_only
from django.contrib import messages
from users.models import User
from django.views.generic import FormView
from django.contrib.auth import login
from .forms import SignupForm, LoginForm
from django.core.mail import send_mail
from django.conf import settings


@method_decorator(guest_only, name="dispatch")
class CustomLoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy("user:dashboard")

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return reverse_lazy("admin:dashboard")
        return reverse_lazy("user:dashboard")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            login(self.request, user)

            send_mail(
                "New Login to Your Account – Was This You?",  # Subject
                "Your account was logged into. If this wasn't you, please contact support.",  # Plain-text message
                settings.DEFAULT_EMAIL,
                [email],  # Recipient list
            )
        messages.error(self.request, "Invalid email or password")
        return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SignupView(FormView):
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("user:dashboard")

    def form_valid(self, form):
        user = form.save()  # The form handles saving
        login(self.request, user)

        send_mail(
            "Welcome to OptionsTradezHub!",  # Subject
            "Thank you for joining OptionsTradezHub! We're excited to have you on board.",  # Plain-text message
            settings.DEFAULT_EMAIL,
            [user.email],  # Recipient list
        )
        messages.success(self.request, "Registration successful")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ref"] = self.request.GET.get("ref")
        return context


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("auth:login")
