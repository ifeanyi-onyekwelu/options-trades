from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse
from .decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from users.models import UserWallet, User
from app.models import (
    Deposit as DepositModel,
    Withdraw as WithdrawModel,
    UserInvestment,
    Notification,
)
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Sum
from .forms import DepositForm
import uuid
from app.utils import create_notification


@method_decorator(login_required, name="dispatch")
class Dashboard(TemplateView):
    template_name = "user/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet = UserWallet.objects.get(user=self.request.user)

        context["wallet"] = wallet
        return context


@method_decorator(login_required, name="dispatch")
class BuyNow(TemplateView):
    template_name = "user/buy-now.html"


@method_decorator(login_required, name="dispatch")
class CopyTrade(TemplateView):
    template_name = "user/copy-trade.html"


@method_decorator(login_required, name="dispatch")
class Deposit(FormView):
    template_name = "user/deposit.html"
    form_class = DepositForm
    success_url = reverse_lazy("user:deposit-confirmation")

    def form_valid(self, form):
        method = form.cleaned_data["method"]
        amount = form.cleaned_data["amount"]

        # Store in session (so it's available in the next view)
        self.request.session["deposit_method"] = method
        self.request.session["deposit_amount"] = str(amount)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("user:deposit-confirmation")


@method_decorator(login_required, name="dispatch")
class DepositConfirmationView(TemplateView):
    template_name = "user/deposit_confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get data from session
        context["method"] = self.request.session.get("deposit_method")
        context["amount"] = self.request.session.get("deposit_amount")

        # Optional: handle case where session data is missing (e.g., user refreshes after session expires)
        if not context["method"] or not context["amount"]:
            context["error"] = "No deposit information found. Please start again."

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the 'I Have Made Payment' button click.
        """
        method = request.session.get("deposit_method")
        amount = request.session.get("deposit_amount")

        if not method or not amount:
            messages.error(
                request,
                "Session expired or missing data. Please start the deposit process again.",
            )
            return redirect("deposit_start")  # Adjust this to the appropriate view

        # Map method to the choices in Deposit.CRYPTO_CHOICES
        method_mapping = {
            "BITCOIN": "BTC",
            "ETHEREUM": "ETH",
            "USDT": "USDT",
            "LITECOIN": "LTC",
        }

        crypto_currency = method_mapping.get(method.upper())

        if not crypto_currency:
            messages.error(request, "Invalid payment method.")
            return redirect("user:deposit")

        deposit = DepositModel.objects.create(
            user=request.user,
            amount=amount,
            crypto_currency=crypto_currency,
            transaction_id=str(uuid.uuid4())[:20],
        )

        # Create Notification
        create_notification(
            user=request.user,
            title="Account Funding",
            description=f"You initiated a deposit of ${amount} using {crypto_currency}. Awaiting verification.",
        )

        messages.success(
            request,
            "Deposit record created successfully! Your wallet will be credited after verification.",
        )

        # Clear the session data after saving
        request.session.pop("deposit_method", None)
        request.session.pop("deposit_amount", None)

        return redirect("user:deposit_history")


@method_decorator(login_required, name="dispatch")
class DepositHistory(TemplateView):
    template_name = "user/deposit-history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deposits = DepositModel.objects.filter(user=self.request.user)

        context["deposits"] = deposits
        return context


@method_decorator(login_required, name="dispatch")
class Withdraw(TemplateView):
    template_name = "user/new-request.html"


@method_decorator(login_required, name="dispatch")
class Invest(TemplateView):
    template_name = "user/invest.html"


@method_decorator(login_required, name="dispatch")
class Broker(TemplateView):
    template_name = "user/broker.html"


# @login_required
# @require_POST
# def handle_invest(request):
#     amount = request.POST.get('amount')

#     user_balance = UserWallet.objects.get(user=request.user)
#     amount_decimal = Decimal(str(amount))

#     if amount_decimal <= 5000:
#         plan_slug = 'starter'
#     elif amount_decimal <= 10000:
#         plan_slug = 'silver'
#     elif amount_decimal <= 50000:
#         plan_slug = 'gold'
#     else:
#         messages.error(request, 'Invalid amount for investment.')
#         return redirect("user:invest")

#     if user_balance.balance < amount_decimal:
#         messages.error(request, 'Insufficient funds.')
#         return redirect("user:invest")

#     investment_plan = get_object_or_404(InvestmentPlan, slug=plan_slug)


#     UserInvestment.objects.create(
#         user=request.user,
#         investment_plan=investment_plan,
#         amount=amount_decimal
#     )

#     user_balance.balance -= amount_decimal
#     user_balance.save()

#     messages.error(request, 'Investment successful')
#     return redirect("user:invest")


@login_required
@require_POST
def handle_withdrawal(request):
    wallet = request.POST.get("account")
    amount = request.POST.get("amount")
    walletAddress = request.POST.get("wallet_address")
    coin = request.POST.get("coin")

    UserWallet = UserWallet.objects.get(user=request.user)
    amount_decimal = Decimal(str(amount))

    if UserWallet.balance < amount_decimal:
        return JsonResponse({"status": "error", "message": "Insufficient funds."})

    withdraw = WithdrawModel.objects.create(
        user=request.user,
        amount=amount_decimal,
        status="Pending",
        wallet_address=walletAddress,
        coin=coin,
    )
    # Create Notification
    create_notification(
        user=request.user,
        title="Withdrawal Request",
        description=f"You requested a withdrawal of ${amount} in {coin}. Awaiting approval.",
    )
    return JsonResponse({"status": "success"})


@method_decorator(login_required, name="dispatch")
class Profile(TemplateView):
    template_name = "user/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["user"] = user
        return context

    def post(self, request, *args, **kwargs):
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")

        address = request.POST.get("address")
        country = request.POST.get("country")
        bio = request.POST.get("bio")

        # Update user information
        User.objects.filter(email=request.user.email).update(
            first_name=firstName,
            last_name=lastName,
            address=address,
            country=country,
            bio=bio,
        )

        # Create notification
        create_notification(
            user=request.user,
            title="Profile Updated",
            description="Your profile information was updated successfully.",
        )

        messages.success(request, "Profile updated successfully!")
        return redirect(reverse("user:profile"))


@method_decorator(login_required, name="dispatch")
class Notifications(TemplateView):
    template_name = "user/notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["notifications"] = Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
        return context


@method_decorator(login_required, name="dispatch")
class Support(TemplateView):
    template_name = "user/support.html"


@method_decorator(login_required, name="dispatch")
class ChangePassword(TemplateView):
    template_name = "user/change-password.html"

    def post(self, request, *args, **kwargs):
        old_password = request.POST.get("oldPassword")
        new_password = request.POST.get("newPassword")
        password2 = request.POST.get("re-enterPassword")

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect")
            return redirect("change_password")

        if new_password != password2:
            messages.error(request, "Password mismatch")
            return redirect("change_password")

        user.set_password(new_password)
        user.save()

        # Create notification
        create_notification(
            user=request.user,
            title="Password Changed",
            description="Your account password was successfully changed.",
        )

        messages.success(request, "Password changed successfully!")
        return redirect("user:change_password")


@method_decorator(login_required, name="dispatch")
class Pin(TemplateView):
    template_name = "user/pin.html"


@method_decorator(login_required, name="dispatch")
class Wallet(TemplateView):
    template_name = "user/wallet.html"


@method_decorator(login_required, name="dispatch")
class Referrals(TemplateView):
    template_name = "user/referrals.html"


@method_decorator(login_required, name="dispatch")
class TransactionHistory(TemplateView):
    template_name = "user/transaction-history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
