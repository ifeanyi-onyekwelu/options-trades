from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    View,
    FormView,
)
from django.utils.decorators import method_decorator
from users.models import User, UserWallet
from app.models import Withdraw, Deposit, Notification
from django.contrib import messages
from .decorators import login_required
from .forms import AdminEmailForm, AddRemoveFundsForm
from django.core.mail import send_mail
from django.conf import settings


def update_user_status(user_id, status):
    user = User.objects.get(id=user_id)
    user.is_active = status
    user.save()


@method_decorator(login_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "user_admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["deposits"] = Deposit.objects.order_by("-date_created")[:5]
        return context


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "user_admin/profile.html")

    def post(self, request, *args, **kwargs):
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")

        address = request.POST.get("address")
        country = request.POST.get("country")

        user = User.objects.filter(email=request.user.email).update(
            first_name=firstName, last_name=lastName, address=address, country=country
        )

        return redirect(reverse("admin:profile"))


@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    template_name = "user_admin/user/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        # Exclude superusers and staff (admins) from the list
        return User.objects.filter(is_superuser=False, is_staff=False)


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
class UserWalletListView(ListView):
    model = UserWallet
    template_name = "user_admin/user_balance/user_balance_list.html"
    context_object_name = "user_balances"


@method_decorator(login_required, name="dispatch")
class UserWalletDetailsView(DetailView):
    model = UserWallet
    template_name = "user_admin/user_balance/user_balance_details.html"
    context_object_name = "user_balance"


@method_decorator(login_required, name="dispatch")
class UserWalletUpdateView(UpdateView):
    model = UserWallet
    template_name = "user_admin/user_balance/user_balance_form.html"
    fields = ["balance"]  # Fields you want to include in the form
    success_url = reverse_lazy(
        "user_admin:user-balance-list"
    )  # Redirect to the user balance list after update


@method_decorator(login_required, name="dispatch")
class UserWalletDeleteView(DeleteView):
    model = UserWallet
    template_name = "user_admin/user_balance/user_balance_confirm_delete.html"
    success_url = reverse_lazy("user_admin:user-balance-list")


def manage_user_funds(request, pk):
    user_balance = get_object_or_404(UserWallet, pk=pk)

    if request.method == "POST":
        form = AddRemoveFundsForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data["amount"]
            action = form.cleaned_data["action"]

            if action == "add":
                user_balance.balance += amount
                messages.success(
                    request,
                    f"{amount} added to the user balance. New balance: {user_balance.balance}",
                )
            elif action == "remove" and user_balance.balance >= amount:
                user_balance.balance -= amount
                messages.success(
                    request,
                    f"{amount} removed from the user balance. New balance: {user_balance.balance}",
                )
            else:
                messages.error(request, "Insufficient funds to remove.")

            user_balance.save()
            return redirect("admin:user-wallet-details", user_balance.id)
    else:
        form = AddRemoveFundsForm()

    return render(
        request,
        "user_admin/user_balance/manage_user_funds.html",
        {"form": form, "user_balance": user_balance},
    )


# -----------------------------
# Deposit Views
# -----------------------------


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


@method_decorator(login_required, name="dispatch")
class DepositUpdateView(UpdateView):
    model = Deposit
    template_name = "user_admin/deposit/deposit_form.html"
    fields = ["status"]  # Only allow updating status

    def form_valid(self, form):
        # Get the current status of the deposit
        deposit = form.save(commit=False)
        previous_status = deposit.status

        print(previous_status)

        # Save the deposit with the new status
        deposit.save()

        # Check if the status is changed to 'approved'
        if deposit.status == "APPROVED":
            print("Hello World")
            # Add the deposit amount to the user's balance
            user_balance = get_object_or_404(UserWallet, user=deposit.user)
            user_balance.balance += deposit.amount
            user_balance.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("admin:deposit-detail", args=[self.object.id])


@method_decorator(login_required, name="dispatch")
class DepositDeleteView(DeleteView):
    model = Deposit
    template_name = "user_admin/deposit/deposit_confirm_delete.html"
    success_url = reverse_lazy("admin:deposits")  # Redirect after deletion


# -----------------------------
# Withdrawal Views
# -----------------------------


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
class WithdrawUpdateView(UpdateView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_form.html"
    fields = ["status"]  # Only allow updating status

    def get_success_url(self):
        return reverse_lazy("admin:withdrawal", args=[self.object.id])


@method_decorator(login_required, name="dispatch")
class WithdrawDeleteView(DeleteView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_confirm_delete.html"
    success_url = reverse_lazy("admin:withdrawals")


@method_decorator(login_required, name="dispatch")
class AdminEmailView(FormView):
    template_name = "user_admin/admin_email_form.html"
    form_class = AdminEmailForm
    success_url = reverse_lazy("admin-email")  # Adjust to your URL name

    def form_valid(self, form):
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        # Get all users excluding admins
        recipients = User.objects.filter(
            is_superuser=False, is_staff=False
        ).values_list("email", flat=True)

        print(recipients)

        # Send email
        if recipients:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                list(recipients),
                fail_silently=False,
            )
            messages.success(self.request, "Emails sent successfully!")
        else:
            messages.warning(self.request, "No users to send emails to.")

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class NotificationsListView(ListView):
    model = Notification
    template_name = "user_admin/notifications.html"
    context_object_name = "notifications"
