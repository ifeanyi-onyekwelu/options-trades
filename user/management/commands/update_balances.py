from django.core.management.base import BaseCommand
from user.balance_updater import update_user_balances

class Command(BaseCommand):
    help = 'Update user balances based on daily returns'

    def handle(self, *args, **options):
        update_user_balances()
        self.stdout.write(self.style.SUCCESS('Successfully updated user balances.'))