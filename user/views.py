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
    Notification,
)
from decimal import Decimal
from django.contrib import messages
from .forms import DepositForm
import uuid
from app.utils import create_notification
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings


STOCKS = {
    1: {"name": "Apple Inc.", "price": 1558.00},
    2: {"name": "Amazon.com, Inc.", "price": 1430.00},
    3: {"name": "Alphabet Inc.", "price": 320.00},
    4: {"name": "Meta Platforms, Inc.", "price": 1440.10},
    5: {"name": "Microsoft Corporation", "price": 1976.00},
    6: {"name": "NVIDIA Corporation", "price": 1440.10},
    7: {"name": "Tesla, Inc. Common Stock", "price": 1440.10},
    8: {"name": "Walmart Inc. Common Stock", "price": 680.30},
}


@method_decorator(login_required, name="dispatch")
class Dashboard(TemplateView):
    template_name = "user/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all wallets associated with the current user
        wallets = UserWallet.objects.filter(user=self.request.user)

        # Fetch the 5 most recent deposits for the user
        deposits = DepositModel.objects.filter(user=self.request.user).order_by(
            "-date_created"
        )[:5]

        context["wallets"] = wallets
        context["deposits"] = deposits
        return context


@method_decorator(login_required, name="dispatch")
class BuyNow(TemplateView):
    template_name = "user/buy-now.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user's wallets and balances
        user_wallets = UserWallet.objects.filter(user=self.request.user)
        context["user_wallets"] = user_wallets
        context["stocks"] = STOCKS
        return context

    def post(self, request, *args, **kwargs):
        # Get the form data
        paytype = request.POST.get(
            "paytype"
        )  # Selected wallet type (e.g., "USDT", "BTC", etc.)
        stock_id = int(request.POST.get("stock"))  # Selected stock ID
        quantity = int(request.POST.get("quantity"))  # Selected quantity (slots)

        # Calculate the total cost for the stock purchase
        stock = STOCKS.get(stock_id)
        if not stock:
            messages.error(request, "Invalid stock selected.")
            return redirect("user:buy-now")

        total_cost = stock["price"] * quantity  # Total cost of the stock

        # Get the wallet the user selected
        wallet = UserWallet.objects.filter(user=request.user, currency=paytype).first()
        if not wallet:
            messages.error(request, "Wallet not found.")
            return redirect("user:buy-now")

        # Check if the user has sufficient balance
        if wallet.balance < total_cost:
            messages.error(
                request,
                f"Insufficient funds. You need ${total_cost - wallet.balance} more.",
            )
            return redirect("user:buy-now")

        # Deduct the amount from the user's wallet
        wallet.balance -= total_cost
        wallet.save()

        # Create a notification for the user
        create_notification(
            user=request.user,
            title="Stock Purchase",
            description=f"You purchased {quantity} slot(s) of {stock['name']} for ${total_cost} using {paytype}.",
        )

        # Redirect to a confirmation page or show a success message
        messages.success(
            request, f"Successfully purchased {quantity} slot(s) of {stock['name']}!"
        )
        return redirect("user:buy-now")  # Or another confirmation page URL


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

        # Send Email Notification
        subject = "Deposit Initiated"
        message = f"Hello {request.user.username},\n\nYou have initiated a deposit of ${amount} using {crypto_currency}. Your transaction is currently pending verification."
        send_mail(subject, message, settings.DEFAULT_EMAIL, [request.user.email])

        # Send Email to Admin
        admin_subject = "New Deposit Request"
        admin_message = f"User {request.user.username} has initiated a deposit of ${amount} using {crypto_currency}. Please verify."
        send_mail(
            admin_subject,
            admin_message,
            settings.DEFAULT_EMAIL,
            [settings.DEFAULT_EMAIL],
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the user's wallets and balances
        user_wallets = UserWallet.objects.filter(user=self.request.user)

        # Check if the user has any wallet with a balance greater than zero
        has_balance = any(wallet.balance > Decimal("0.00") for wallet in user_wallets)

        context["user_wallets"] = user_wallets
        context["has_balance"] = has_balance  # Add this to check balance presence

        return context

    def post(self, request, *args, **kwargs):
        # Retrieve form data
        wallet_id = request.POST.get("wallet")
        wallet_address = request.POST.get("wallet_address")
        amount = Decimal(request.POST.get("amount"))

        # Retrieve the selected wallet
        try:
            wallet = UserWallet.objects.get(user=request.user, currency=wallet_id)
        except UserWallet.DoesNotExist:
            messages.error(request, "Wallet not found.")
            return redirect("user:withdraw")

        # Check if the user has sufficient balance
        if wallet.balance < amount:
            messages.error(request, "Insufficient balance.")
            return redirect("user:withdraw")

        # Start a transaction to ensure consistency
        with transaction.atomic():
            withdrawal = WithdrawModel.objects.create(
                user=request.user,
                amount=amount,
                wallet_address=wallet_address,
                wallet=wallet,
                status="Pending",
            )

            # Send Email Notification
            subject = "Withdrawal Request Submitted"
            message = f"Hello {request.user.username},\n\nYou have requested a withdrawal of ${amount} to the wallet address {wallet_address}. Your request is currently pending approval."
            send_mail(subject, message, settings.DEFAULT_EMAIL, [request.user.email])

            # Send Email to Admin
            admin_subject = "New Withdrawal Request"
            admin_message = f"User {request.user.username} has requested a withdrawal of ${amount} to {wallet_address}. Please review and approve."
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_EMAIL,
                [settings.DEFAULT_EMAIL],
            )

            create_notification(
                user=request.user,
                title="Withdrawal Request",
                description=f"You requested a withdrawal of ${amount} to the wallet address {wallet_address}.",
            )
        return redirect("user:withdraw_history")


@method_decorator(login_required, name="dispatch")
class WithdrawHistory(TemplateView):
    template_name = "user/withdraw-history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        withdrawals = WithdrawModel.objects.filter(user=self.request.user)

        context["withdrawals"] = withdrawals
        return context


@method_decorator(login_required, name="dispatch")
class Invest(TemplateView):
    template_name = "user/invest.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user's wallets and balances
        user_wallets = UserWallet.objects.filter(user=self.request.user)
        context["user_wallets"] = user_wallets
        context["stocks"] = STOCKS
        return context

    def post(self, request, *args, **kwargs):
        # Get the form data
        paytype = request.POST.get(
            "paytype"
        )  # Selected wallet type (e.g., "USDT", "BTC", etc.)
        stock_id = int(request.POST.get("stock"))  # Selected stock ID
        quantity = int(request.POST.get("quantity"))  # Selected quantity (slots)

        # Calculate the total cost for the stock purchase
        stock = STOCKS.get(stock_id)
        if not stock:
            messages.error(request, "Invalid stock selected.")
            return redirect("user:invest")

        total_cost = stock["price"] * quantity  # Total cost of the stock

        # Get the wallet the user selected
        wallet = UserWallet.objects.filter(user=request.user, currency=paytype).first()
        if not wallet:
            messages.error(request, "Wallet not found.")
            return redirect("user:invest")

        if wallet.balance < total_cost:
            messages.error(
                request,
                f"Insufficient funds. You need ${total_cost - float(wallet.balance):.2f} more.",
            )
            return redirect("user:invest")

        total_cost_decimal = Decimal(str(total_cost))

        # Deduct the amount from the user's wallet
        wallet.balance -= total_cost_decimal
        wallet.save()

        # Create a notification for the user
        create_notification(
            user=request.user,
            title="Stock Purchase",
            description=f"You purchased {quantity} slot(s) of {stock['name']} for ${total_cost} using {paytype}.",
        )

        # Redirect to a confirmation page or show a success message
        messages.success(
            request, f"Successfully purchased {quantity} slot(s) of {stock['name']}!"
        )
        return redirect("user:invest")  # Or another confirmation page URL


@method_decorator(login_required, name="dispatch")
class Broker(TemplateView):
    template_name = "user/broker.html"

    def post(self, request, *args, **kwargs):
        messages.error(request, "Invalid hash!")
        return redirect(reverse("user:broker"))


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
