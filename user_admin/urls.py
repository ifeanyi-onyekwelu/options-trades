from django.urls import path
from .views import *

app_name = "admin"

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # users
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', UserDetailsView.as_view(), name='user-details'),
    path('users/suspend/<uuid:user_id>/', mark_user_as_suspended, name='suspend-user'),
    path('users/activate/<uuid:user_id>/', mark_user_as_active, name='activate-user'),

    # user profiles
    path('user-profiles/', UserProfileListView.as_view(), name='user-profile-list'),
    path('user-profile/<uuid:pk>/', UserProfileDetailsView.as_view(), name='user-profile-details'),
    path('user-profile/<uuid:pk>/delete/', UserProfileDeleteView.as_view(), name='user-profile-delete'),

    # users balance
    path('user-balances/', UserBalanceListView.as_view(), name='user-balance-list'),
    path('user-balance/<uuid:pk>/', UserBalanceDetailsView.as_view(), name='user-balance-details'),
    path('user-balance/<uuid:pk>/delete/', UserBalanceDeleteView.as_view(), name='user-balance-delete'),

    # investments
    path('investment_plans/', InvestmentPlanListView.as_view(), name='investment_plans'),
    path('investment_plans/<uuid:pk>/', InvestmentPlanDetailView.as_view(), name='investment_plan'),
    path('investment_plans/<uuid:pk>/update/', InvestmentPlanUpdateView.as_view(), name='investment_plan-edit'),
    path('investment_plans/create/', InvestmentPlanCreateView.as_view(), name='investment_plan-create'),
    path('investment_plans/<uuid:pk>/delete/', delete_investment, name='investment_plan-delete'),

    # deposits
    path('deposits/', DepositListView.as_view(), name='deposits'),
    path('deposits/<uuid:pk>/', DepositDetailView.as_view(), name='deposit'),
    path('deposits/<uuid:pk>/delete/', delete_deposit, name='deposit-delete'),

    # withdrawals
    path('withdrawals/', WithdrawListView.as_view(), name='withdrawals'),
    path('withdrawals/<uuid:pk>/', WithdrawDetailView.as_view(), name='withdrawal'),
    path('withdrawals/<uuid:pk>/update/', WithdrawUpdateView.as_view(), name='withdrawal-edit'),
    path('withdrawal/<uuid:withdraw_id>/delete/', delete_withdrawal, name='delete-withdrawal'),

    # transfers
    path('transfers/', TransferListView.as_view(), name='transfers'),
    path('transfers/<uuid:pk>/', TransferDetailView.as_view(), name='transfer'),
    path('transfers/<uuid:pk>/delete/', delete_transfer, name='transfer-delete'),

    # auth
    path('login/', Login.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', handle_logout, name='logout')
]