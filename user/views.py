from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .decorators import login_required
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from users.models import UserProfile, UserBalance, User
from app.models import Deposit as DepositModel, Transfer as TransferModel, Withdraw as WithdrawModel, InvestmentPlan, UserInvestment
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum


@method_decorator(login_required, name="dispatch")
class Dashboard(TemplateView):
    template_name = 'user/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['profile'] = UserProfile.objects.get(user=self.request.user)
        context['balance'] = UserBalance.objects.get(user=self.request.user)
        context['total_referrals'] = UserProfile.objects.filter(referred_by=self.request.user).count()
        context['total_withdrawal'] = WithdrawModel.objects.filter(user=self.request.user).count()

        # Calculate total invested amount and returns
        total_invested = UserInvestment.objects.filter(user=self.request.user).aggregate(total_invested=Sum('amount'))['total_invested'] or 0

        context['total_invested'] = total_invested

        return context


@method_decorator(login_required, name="dispatch")
class BuyNow(TemplateView):
    template_name = 'user/buy-now.html'


@method_decorator(login_required, name="dispatch")
class CopyTrade(TemplateView):
    template_name = 'user/copy-trade.html'


@method_decorator(login_required, name="dispatch")
class Deposit(TemplateView):
    template_name = 'user/deposit.html'


@method_decorator(login_required, name="dispatch")
class Withdraw(TemplateView):
    template_name = 'user/new-request.html'


@method_decorator(login_required, name="dispatch")
class Invest(TemplateView):
    template_name = 'user/invest.html'
    
@method_decorator(login_required, name="dispatch")
class Broker(TemplateView):
    template_name = 'user/broker.html'


# @login_required
# @require_POST
# def handle_invest(request):
#     amount = request.POST.get('amount')

#     user_balance = UserBalance.objects.get(user=request.user)
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
    wallet = request.POST.get('account')
    amount = request.POST.get('amount')
    walletAddress = request.POST.get('wallet_address')
    coin = request.POST.get('coin')

    userBalance = UserBalance.objects.get(user=request.user)
    amount_decimal = Decimal(str(amount))

    if userBalance.balance < amount_decimal:
        return JsonResponse({'status': 'error', 'message': 'Insufficient funds.'})

    withdraw = WithdrawModel.objects.create(
        user=request.user,
        amount=amount_decimal,
        status="Pending",
        wallet_address=walletAddress,
        coin=coin
    )
    return JsonResponse({'status': 'success'})


@method_decorator(login_required, name="dispatch")
class Profile(TemplateView):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['profile'] = UserProfile.objects.get(user=self.request.user)

        return context

@method_decorator(login_required, name="dispatch")
class Notifications(TemplateView):
    template_name = 'user/notifications.html'
    
@method_decorator(login_required, name="dispatch")
class Support(TemplateView):
    template_name = 'user/support.html'


@login_required
@require_POST
def handle_update_profile(request):
    firstName = request.POST.get('firstName')
    lastName = request.POST.get('lastName')
    userName = request.POST.get('userName')
    email = request.POST.get('email')
    phone = request.POST.get('phoneNumber')

    address = request.POST.get('address')
    state =  request.POST.get('state')
    zipcode = request.POST.get('zipcode')
    country = request.POST.get('country')

    profile_image = request.FILES.get('profile_img')

    
    if request.user.username != userName:
        if User.objects.filter(username=userName).exists():
            return JsonResponse({'status': 'error', 'message': 'Username is not available'})

    if request.user.email != email:
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email address is not available'})

    if request.user.phone_number != phone:
        if User.objects.filter(phone_number=phone).exists():
            return JsonResponse({'status': 'error', 'message': 'Phone number is linked to a different account'})
        
    user = User.objects.filter(email=request.user.email).update(first_name=firstName, last_name=lastName, phone_number=phone, email=email, username=userName)

    userProfile = UserProfile.objects.filter(user=request.user).update(address=address, state=state, zipcode=zipcode, country=country)

    return JsonResponse({'status': 'success'})


@method_decorator(login_required, name="dispatch")
class ChangePassword(TemplateView):
    template_name = 'user/change-password.html'
    
@method_decorator(login_required, name="dispatch")
class Pin(TemplateView):
    template_name = 'user/pin.html'
    
@method_decorator(login_required, name="dispatch")
class Wallet(TemplateView):
    template_name = 'user/wallet.html'
    
@method_decorator(login_required, name="dispatch")
class Referrals(TemplateView):
    template_name = 'user/referrals.html'


@login_required
@require_POST
def handle_change_password(request):
    old_password = request.POST.get('oldPassword')
    new_password = request.POST.get('newPassword')
    password2 = request.POST.get('re-enterPassword')

    user = User.objects.get(email=request.user.email)

    if not user.check_password(old_password):
        return JsonResponse({'status': 'error', 'message': 'Old password is incorrect'})
    
    if new_password != password2:
        return JsonResponse({'status': 'error', 'message': 'Password mismatch'})

    user.password = make_password(password=new_password)
    user.save()
    return JsonResponse({'status': 'success'})


@method_decorator(login_required, name="dispatch")
class TransactionHistory(TemplateView):
    template_name = 'user/transaction-history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve recent deposits, withdrawals, and transfers
        recent_deposits = DepositModel.objects.filter(user=self.request.user)
        recent_withdrawals = WithdrawModel.objects.filter(user=self.request.user)
        recent_transfers = TransferModel.objects.filter(sender=self.request.user)
        recent_transfers2 = TransferModel.objects.filter(receiver=self.request.user)

        all_transactions = sorted(
            list(recent_deposits) + list(recent_withdrawals) + list(recent_transfers) + list(recent_transfers2),
            key=lambda x: x.date_created,
            reverse=True
        )

        context['all_transactions'] = all_transactions
        return context


@method_decorator(login_required, name="dispatch")
class ReferredUsers(TemplateView):
    template_name = 'user/referred-users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve referred users
        referred_users = UserProfile.objects.filter(referred_by=self.request.user)

        context['referred_users'] = referred_users

        return context
