from django.urls import path
from .views import *

app_name = 'user'

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('agreement/', BuyNow.as_view(), name='buy-now'),
    path('start/', CopyTrade.as_view(), name='copy-trade'),
    path('invest/', Investment.as_view(), name='invest'),
    # path('handle-invest/', handle_invest, name='handle-invest'),
    path('deposit/', Deposit.as_view(), name='deposit'),
    path('withdraw/', Withdraw.as_view(), name='withdraw'),
    path('handle-withdraw/', handle_withdrawal, name='handle-withdraw'),
    path('transaction-history/', TransactionHistory.as_view(), name='transaction-history'),
    path('referred-users/', ReferredUsers.as_view(), name='referred-users'),
    path('transfer-funds/', TransferFunds.as_view(), name='transfer-funds'),
    path('profile/', Profile.as_view(), name='profile'),
    path('update-profile/', handle_update_profile, name='update-profile'),
    path('change-password/', ChangePassword.as_view(), name='change-password'),
    path('handle-change-password/', handle_change_password, name='handle-change-password'),
    path('delete-account/', delete_account, name='delete-account'),
]