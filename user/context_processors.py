from users.models import UserWallet


def total_balance_user(request):
    """Returns the total balance across all wallets of the currently logged-in user"""
    user_balance = 0
    if request.user.is_authenticated:
        # Get all wallets associated with the user
        user_wallets = UserWallet.objects.filter(user=request.user)
        # Sum the balance of all wallets
        user_balance = sum(wallet.balance for wallet in user_wallets)
    return {"total_balance_user": user_balance}
