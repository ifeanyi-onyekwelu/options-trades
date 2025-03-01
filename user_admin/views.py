from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    View,
)
from django.utils.decorators import method_decorator
from users.models import User, UserProfile, UserBalance
from app.models import Withdraw, Deposit, InvestmentPlan, Transfer, UserInvestment
from django.contrib import messages
from .decorators import login_required, guest_only
from django.views.decorators.http import require_POST
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import InvestmentPlanForm


def update_user_status(user_id, status):
    user = User.objects.get(id=user_id)
    user.is_active = status
    user.save()


@method_decorator(login_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "user_admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["users_count"] = User.objects.all().count()
        context["deposit_count"] = Deposit.objects.all().count()
        context["withdraw_count"] = Withdraw.objects.all().count()
        context["investment_active_count"] = UserInvestment.objects.all().count()

        recent_users = User.objects.order_by("-date_joined")[:10]
        context["recent_users"] = recent_users

        withrawals = Withdraw.objects.order_by("-date_created")[:10]
        deposit = Deposit.objects.order_by("-date_created")[:10]
        transfer = Transfer.objects.order_by("-date_created")[:10]
        userInvestment = UserInvestment.objects.order_by("-date_created")[:10]
        investmentPlans = InvestmentPlan.objects.order_by("-date_created")[:10]

        all_timeline = sorted(
            list(withrawals)
            + list(deposit)
            + list(transfer)
            + list(userInvestment)
            + list(investmentPlans),
            key=lambda x: x.date_created,
            reverse=True,
        )

        all_transactions = sorted(
            list(withrawals) + list(deposit) + list(transfer),
            key=lambda x: x.date_created,
            reverse=True,
        )

        context["all_timeline"] = all_timeline
        context["all_transactions"] = all_transactions

        return context


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "user_admin/profile.html")

    def post(self, request, *args, **kwargs):
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        userName = request.POST.get("userName")
        email = request.POST.get("email")
        phone = request.POST.get("phoneNumber")

        address = request.POST.get("address")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")
        country = request.POST.get("country")

        if request.user.username != userName:
            if User.objects.filter(username=userName).exists():
                messages.error(request, "Username is not available")
                return redirect(reverse("admin:profile"))

        if request.user.email != email:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email address is not available")
                return redirect(reverse("admin:profile"))

        if request.user.phone_number != phone:
            if User.objects.filter(phone_number=phone).exists():
                messages.error(request, "Phone number is linked to a different account")
                return redirect(reverse("admin:profile"))

        user = User.objects.filter(email=request.user.email).update(
            first_name=firstName,
            last_name=lastName,
            phone_number=phone,
            email=email,
            username=userName,
        )
        userProfile = UserProfile.objects.filter(user=request.user).update(
            address=address, state=state, zipcode=zipcode, country=country
        )
        return redirect(reverse("admin:profile"))


@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    template_name = "user_admin/user/user_list.html"
    context_object_name = "users"


@login_required
def mark_user_as_active(request, user_id):
    update_user_status(user_id, True)
    return redirect("admin:user-list")


@login_required
def mark_user_as_suspended(request, user_id):
    update_user_status(user_id, False)
    return redirect("admin:user-list")


@method_decorator(login_required, name="dispatch")
class UserDetailsView(DetailView):
    model = User
    template_name = "user_admin/user/user_details.html"
    context_object_name = "user"


@method_decorator(login_required, name="dispatch")
class UserDeleteView(DeleteView):
    model = User
    template_name = "user_admin/user/user_confirm_delete.html"
    success_url = reverse_lazy(
        "user_admin:user-list"
    )  # Redirect to the user list after deletion


@method_decorator(login_required, name="dispatch")
class UserBalanceListView(ListView):
    model = UserBalance
    template_name = "user_admin/user_balance/user_balance_list.html"
    context_object_name = "user_balances"


@method_decorator(login_required, name="dispatch")
class UserBalanceDetailsView(DetailView):
    model = UserBalance
    template_name = "user_admin/user_balance/user_balance_details.html"
    context_object_name = "user_balance"


@method_decorator(login_required, name="dispatch")
class UserBalanceUpdateView(UpdateView):
    model = UserBalance
    template_name = "user_admin/user_balance/user_balance_form.html"
    fields = ["balance"]  # Fields you want to include in the form
    success_url = reverse_lazy(
        "user_admin:user-balance-list"
    )  # Redirect to the user balance list after update


@method_decorator(login_required, name="dispatch")
class UserBalanceDeleteView(DeleteView):
    model = UserBalance
    template_name = "user_admin/user_balance/user_balance_confirm_delete.html"
    success_url = reverse_lazy("user_admin:user-balance-list")


@method_decorator(login_required, name="dispatch")
class UserProfileListView(ListView):
    model = UserProfile
    template_name = "user_admin/user_profile/user_profile_list.html"
    context_object_name = "user_profiles"


@method_decorator(login_required, name="dispatch")
class UserProfileDetailsView(DetailView):
    model = UserProfile
    template_name = "user_admin/user_profile/user_profile_details.html"
    context_object_name = "user_profile"


@method_decorator(login_required, name="dispatch")
class UserProfileDeleteView(DeleteView):
    model = UserProfile
    template_name = "user_admin/user_profile/user_profile_confirm_delete.html"
    success_url = reverse_lazy("user_admin:user-profile-list")


@method_decorator(login_required, name="dispatch")
class InvestmentPlanListView(ListView):
    model = InvestmentPlan
    template_name = "user_admin/investment/investment_plan_list.html"
    context_object_name = "investment_plans"


@method_decorator(login_required, name="dispatch")
class InvestmentPlanDetailView(DetailView):
    model = InvestmentPlan
    template_name = "user_admin/investment/investment_plan_detail.html"
    context_object_name = "investment_plan"


@method_decorator(login_required, name="dispatch")
class InvestmentPlanCreateView(CreateView):
    model = InvestmentPlan
    template_name = "user_admin/investment/investment_plan_form.html"
    form_class = InvestmentPlanForm
    success_url = reverse_lazy("admin:investment_plans")


@method_decorator(login_required, name="dispatch")
class InvestmentPlanUpdateView(UpdateView):
    model = InvestmentPlan
    template_name = "user_admin/investment/investment_plan_form.html"
    fields = "__all__"


@login_required
def delete_investment(request, investment_id):
    investment = get_object_or_404(InvestmentPlan, id=investment_id)
    investment.delete()
    return redirect("admin:investment_plans")


@method_decorator(login_required, name="dispatch")
class DepositListView(ListView):
    model = Deposit
    template_name = "user_admin/deposit/deposit_list.html"
    context_object_name = "deposits"


@method_decorator(login_required, name="dispatch")
class DepositDetailView(DetailView):
    model = Deposit
    template_name = "user_admin/deposit/deposit_detail.html"
    context_object_name = "deposit"


@login_required
def delete_deposit(request, deposit):
    deposit = get_object_or_404(Deposit, id=deposit)
    deposit.delete()
    return redirect("admin:deposits")


@method_decorator(login_required, name="dispatch")
class WithdrawListView(ListView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_list.html"
    context_object_name = "withdrawals"


@method_decorator(login_required, name="dispatch")
class WithdrawDetailView(DetailView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_detail.html"
    context_object_name = "withdraw"


@method_decorator(login_required, name="dispatch")
class WithdrawCreateView(CreateView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_form.html"
    fields = "__all__"


@method_decorator(login_required, name="dispatch")
class WithdrawUpdateView(UpdateView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_form.html"
    fields = ["status"]

    def get_success_url(self):
        return reverse_lazy("admin:withdrawal", args=[self.object.id])


@login_required
def delete_withdrawal(request, withdraw_id):
    withdraw = get_object_or_404(Withdraw, id=withdraw_id)
    withdraw.delete()
    return redirect("admin:withdrawals")


@method_decorator(login_required, name="dispatch")
class TransferListView(ListView):
    model = Transfer
    template_name = "user_admin/transfer/transfer_list.html"
    context_object_name = "transfers"


@method_decorator(login_required, name="dispatch")
class TransferDetailView(DetailView):
    model = Transfer
    template_name = "user_admin/transfer/transfer_detail.html"
    context_object_name = "transfer"


@login_required
def delete_transfer(request, transfer_id):
    transfer = get_object_or_404(Transfer, id=transfer_id)
    transfer.delete()
    return redirect("admin:transfers")
