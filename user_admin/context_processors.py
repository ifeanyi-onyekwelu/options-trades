from django.db.models import Sum
from users.models import UserWallet  # Import UserWallet from the user app


def total_balance_admin(request):
    """Returns the total balance of all users for the admin panel"""
    total = UserWallet.objects.aggregate(Sum("balance"))["balance__sum"] or 0
    return {"total_balance_admin": total}
