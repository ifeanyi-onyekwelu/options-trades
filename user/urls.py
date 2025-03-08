from django.urls import path
from .views import *

app_name = 'user'

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('agreement/', BuyNow.as_view(), name='buy-now'),
    path('start/', CopyTrade.as_view(), name='copy-trade'),
    path('invest/', Invest.as_view(), name='invest'),
    path('deposit/', Deposit.as_view(), name='deposit'),
    path('withdraw/', Withdraw.as_view(), name='withdraw'),
    path('broker/', Broker.as_view(), name='broker'),
    path('notifications/', Notifications.as_view(), name='notifications'),
    path('support/', Support.as_view(), name='support'),
    path('transaction-history/', TransactionHistory.as_view(), name='transaction-history'),
    path('profile/', Profile.as_view(), name='profile'),
    path('change-password/', ChangePassword.as_view(), name='change-password'),
    path('pin/', Pin.as_view(), name='pin'),
    path('wallet/', Wallet.as_view(), name='wallet'),
    path('referrals/', Referrals.as_view(), name='referrals'),
    
    # path('handle-invest/', handle_invest, name='handle-invest'),
    path('referred-users/', ReferredUsers.as_view(), name='referred-users'),
]