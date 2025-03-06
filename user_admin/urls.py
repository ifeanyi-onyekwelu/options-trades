from django.urls import path
from .views import *

app_name = "admin"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # users
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<uuid:pk>/", UserDetailsView.as_view(), name="user-details"),
    path("users/suspend/<uuid:user_id>/", mark_user_as_suspended, name="suspend-user"),
    path("users/activate/<uuid:user_id>/", mark_user_as_active, name="activate-user"),
    path("user-wallets/", UserWalletListView.as_view(), name="user-wallet-list"),
    path(
        "user-wallets/<uuid:pk>/",
        UserWalletDetailsView.as_view(),
        name="user-wallet-details",
    ),
    path(
        "user-wallets/<uuid:pk>/delete/",
        UserWalletDeleteView.as_view(),
        name="user-wallet-delete",
    ),
    path("manage-funds/<uuid:pk>/", manage_user_funds, name="manage-funds"),
    # deposits
    path("deposits/", DepositListView.as_view(), name="deposits"),
    path("deposits/<uuid:pk>/", DepositDetailView.as_view(), name="deposit-detail"),
    path(
        "deposits/<uuid:pk>/edit/", DepositUpdateView.as_view(), name="deposit-update"
    ),
    path(
        "deposits/<uuid:pk>/delete/", DepositDeleteView.as_view(), name="deposit-delete"
    ),
    path("withdrawals/", WithdrawListView.as_view(), name="withdrawals"),
    path("withdrawals/<uuid:pk>/", WithdrawDetailView.as_view(), name="withdrawal"),
    path(
        "withdrawals/<uuid:pk>/edit/",
        WithdrawUpdateView.as_view(),
        name="withdrawal-update",
    ),
    path(
        "withdrawals/<uuid:pk>/delete/",
        WithdrawDeleteView.as_view(),
        name="withdrawal-delete",
    ),
    path("compose-mail/", AdminEmailView.as_view(), name="compose-mail"),
    path("notifications.", NotificationsListView.as_view(), name="notifications-list"),
]
