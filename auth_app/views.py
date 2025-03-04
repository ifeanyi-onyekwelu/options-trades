from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from users.models import User, UserProfile
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from .decorators import guest_only, login_required
from django.contrib import messages


@method_decorator(guest_only, name="dispatch")
class Login(TemplateView):
    template_name = "login.html"


@method_decorator(guest_only, name="dispatch")
class Signup(TemplateView):
    template_name = "signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["ref"] = self.request.GET.get("ref")
        return context


@guest_only
@require_POST
def handle_login(request):
    try:
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = get_object_or_404(User, email=email)

        if not user.check_password(password):
            messages.error(request, "Invalid credentials provided!")
            return redirect(reverse("auth:login"))

        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect(reverse("admin:dashboard"))
            else:
                return redirect(reverse("user:dashboard"))
        else:
            messages.error(request, "Invalid credentials provided!")
            return redirect(reverse("auth:login"))
    except Exception as e:
        messages.error(request, "Invalid credentials provided!")
        return redirect(reverse("auth:login"))


@guest_only
@require_POST
def handle_signup(request):
    firstName = request.POST.get("fname")
    lastName = request.POST.get("lname")
    email = request.POST.get("email")
    password = request.POST.get("password1")
    password2 = request.POST.get("password2")

    referral_code = request.POST.get("ref")

    if not password == password2:
        messages.error(request, "Passwords do not match")
        return redirect(reverse("auth:signup"))

    if User.objects.filter(email=email).exists():
        messages.error(request, "Email already exists")
        return redirect(reverse("auth:signup"))

    new_user = User.objects.create(
        first_name=firstName,
        last_name=lastName,
        email=email,
        password=make_password(password),
    )

    try:
        referrer = UserProfile.objects.get(referral_code=referral_code)
        new_user_profile = UserProfile.objects.create(
            user=new_user, referred_by=referrer.user
        )
    except UserProfile.DoesNotExist:
        new_user_profile = UserProfile.objects.create(user=new_user)

    new_user.save()
    new_user_profile.save()

    messages.success(request, "Registration successful")
    return redirect(reverse("user:dashboard"))


@login_required
def handle_logout(request):
    logout(request)
    return redirect(reverse("auth:login"))
