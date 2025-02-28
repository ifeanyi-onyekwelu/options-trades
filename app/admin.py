from django.contrib import admin
from .models import InvestmentPlan, UserInvestment, Deposit, Withdraw, Transfer, Referral

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ('name','starting_price','maximum_price','returns_percentage','duration_days','total_returns_percentage','date_created')

@admin.register(UserInvestment)
class UserInvestmentAdmin(admin.ModelAdmin):
    list_display = ('user','investment_plan','amount', 'returns', 'date_created')

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user','amount','transaction_id','date_created')

@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('user','amount','transaction_id','date_created')

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('sender','receiver','amount','transaction_id','date_created')

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer','referred_user','date_created')
