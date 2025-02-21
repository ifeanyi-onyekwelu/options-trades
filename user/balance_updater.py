import schedule
import time
from app.models import UserInvestment, calculate_returns
from django.utils import timezone

def update_user_balances():
    active_investments = UserInvestment.objects.filter(
        investment_plan__date_created__lte=timezone.now()
    )

    for investment in active_investments:
        daily_returns = calculate_returns(investment.amount, investment.investment_plan)
        investment.user_balance.balance += daily_returns
        investment.user_balance.save()

    print('Successfully updated user balances.')

schedule.every().day.at('00:00').do(update_user_balances)

while True:
    schedule.run_pending()
    time.sleep(1)