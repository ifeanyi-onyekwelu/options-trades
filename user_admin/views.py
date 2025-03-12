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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Sum
from django.db import transaction
from app.utils import create_notification


def update_user_status(user_id, status):
    user = User.objects.get(id=user_id)
    user.is_active = status
    user.save()


@method_decorator(login_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "user_admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get total balance of all users grouped by wallet currency
        wallet_balances = (
            UserWallet.objects.values("currency")
            .annotate(total_balance=Sum("balance"))
            .order_by("currency")
        )

        # Convert to a dictionary for easy template access
        context["wallet_balances"] = {
            wallet["currency"]: wallet["total_balance"] for wallet in wallet_balances
        }

        # Get latest 5 deposits
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

        print(f"Previous status: {previous_status}")

        # Save the deposit with the new status
        deposit.save()

        # Check if the status is changed to 'APPROVED'
        if deposit.status == "APPROVED":
            print("Deposit approved!")

            # Get the wallet based on the method selected (BTC, ETH, USDT, etc.)
            wallet = get_object_or_404(
                UserWallet, user=deposit.user, currency=deposit.crypto_currency
            )

            # Add the deposit amount to the user's selected wallet
            wallet.balance += deposit.amount
            wallet.save()

        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the admin dashboard or a specific URL after processing the deposit
        return reverse_lazy("admin:deposits")  # Adjust according to your URL structure


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
    fields = ["status"]  # Only allow updating the status

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Get the withdrawal instance
        previous_status = self.object.status  # Store previous status
        new_status = request.POST.get("status")  # Get the new status from the form

        # Ensure wallet exists
        wallet = get_object_or_404(
            UserWallet, user=self.object.user, currency=self.object.wallet.currency
        )

        # Start transaction for atomic operations
        with transaction.atomic():
            self.object.status = new_status
            self.object.save()

            # If admin approves the withdrawal and it was previously pending
            if new_status == "Approved" and previous_status == "Pending":
                if wallet.balance >= self.object.amount:
                    wallet.balance -= self.object.amount  # Deduct balance
                    wallet.save()
                    create_notification(
                        user=self.object.user,
                        title="Withdrawal Approved",
                        description=f"Your withdrawal of ${self.object.amount} to {self.object.wallet_address} has been approved.",
                    )
                    messages.success(
                        request, "Withdrawal approved and balance deducted."
                    )
                else:
                    messages.error(
                        request, "Insufficient balance to approve this withdrawal."
                    )
                    return redirect("admin:withdrawal", pk=self.object.id)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("admin:withdrawal", args=[self.object.id])


@method_decorator(login_required, name="dispatch")
class WithdrawDeleteView(DeleteView):
    model = Withdraw
    template_name = "user_admin/withdraw/withdraw_confirm_delete.html"
    success_url = reverse_lazy("admin:withdrawals")


class AdminEmailView(FormView):
    template_name = "user_admin/admin_email_form.html"
    form_class = AdminEmailForm
    success_url = reverse_lazy("admin:compose-mail")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]
        recipient_email = form.cleaned_data["recipient"]

        if recipient_email == "all":
            recipients = User.objects.filter(
                is_superuser=False, is_staff=False
            ).values_list("email", flat=True)
        else:
            recipients = [recipient_email]

        print(recipients)

        context = {
            "user": self.request.user,
            "subject": subject,
            "message": message,
        }

        html_message = render_to_string("user_admin/email_template.html", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipients,
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        messages.success(self.request, "Email sent successfully!")
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class NotificationsListView(ListView):
    model = Notification
    template_name = "user_admin/notifications.html"
    context_object_name = "notifications"
