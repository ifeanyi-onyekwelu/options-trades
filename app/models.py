from django.db import models
from django.contrib.auth import get_user_model
import uuid
<<<<<<< HEAD
import datetime
from django.utils import timezone
=======
from django.utils.timezone import now
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6
import secrets
import string
from decimal import Decimal
from users.models import UserBalance
from django.utils.text import slugify
import os

<<<<<<< HEAD
now = timezone.now()
naive_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)
aware_datetime = timezone.make_aware(naive_datetime, timezone=timezone.get_current_timezone())

=======
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6
def default_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('profile images', filename)


def calculate_returns(amount, investment_plan):
    daily_returns = (investment_plan.returns_percentage / 100) * amount
    total_returns = daily_returns * investment_plan.duration_days

    return round(total_returns, 2)


class InvestmentPlan(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    maximum_price = models.DecimalField(max_digits=10, decimal_places=2)
    returns_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.IntegerField()
    total_returns_percentage = models.DecimalField(max_digits=5, decimal_places=2)
<<<<<<< HEAD
    date_created = models.DateTimeField(default=aware_datetime)
=======
    date_created = models.DateTimeField(default=now)
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6

    def __str__(self):
        return "{}".format(self.name)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
    
    @property
    def get_type(self):
        return 'investment_plan'


class UserInvestment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    investment_plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    returns = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
<<<<<<< HEAD
    date_created = models.DateTimeField(default=aware_datetime)
=======
    date_created = models.DateTimeField(default=now)
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6

    def __str__(self):
        return "Investment by {}. Plan - {}".format(self.user, self.investment_plan)

    def save(self, *args, **kwargs):
        returns = calculate_returns(self.amount, self.investment_plan)

        self.returns = returns

        super().save(*args, **kwargs)

    @property
    def get_type(self):
        return 'user_investment'


class Deposit(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=20, unique=True)
    proof_of_payment = models.FileField(upload_to="proof of payment/", null=True)
<<<<<<< HEAD
    date_created = models.DateTimeField(default=aware_datetime)
=======
    date_created = models.DateTimeField(default=now)
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6
    
    def generate_transaction_id(self):
        transaction_id = ''.join(secrets.choice(string.digits) for x in range(20))
        return transaction_id

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        user_balance = UserBalance.objects.get(user=self.user)
        user_balance.balance += self.amount
        user_balance.save()
        
        super().save(*args, **kwargs)

    @property
    def transaction_type(self):
        return 'deposit'


class Withdraw(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'), 
        ('Successul', 'Successful'), 
        ('Failed', 'Failed')
    )
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=20, unique=True)
    wallet_address = models.CharField(max_length=100, default="0")
    coin = models.CharField(max_length=100, default="USDT")
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
<<<<<<< HEAD
    date_created = models.DateTimeField(default=aware_datetime)
=======
    date_created = models.DateTimeField(default=now)
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6

    def generate_transaction_id(self):
        transaction_id = ''.join(secrets.choice(string.digits) for x in range(20))
        return transaction_id

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        # Deduct the withdraw amount from the UserBalance
        user_balance = UserBalance.objects.get(user=self.user)
        user_balance.balance -= self.amount
        user_balance.save()
        print(self.amount)
        
        super().save(*args, **kwargs)

    @property
    def transaction_type(self):
        return 'withdrawal'


class Transfer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    sender = models.ForeignKey(get_user_model(), related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(get_user_model(), related_name='receiver', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=20, unique=True)
<<<<<<< HEAD
    date_created = models.DateTimeField(default=aware_datetime)
=======
    date_created = models.DateTimeField(default=now)
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6

    def generate_transaction_id(self):
        transaction_id = ''.join(secrets.choice(string.digits) for x in range(20))
        return transaction_id

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        amount_decimal = Decimal(str(self.amount))        

        user_balance = UserBalance.objects.get(user=self.sender)
        sender_balance = UserBalance.objects.get(user=self.receiver)
        user_balance.balance -= amount_decimal
        sender_balance.balance += amount_decimal
        user_balance.save()
        sender_balance.save()
        
        super().save(*args, **kwargs)

    @property
    def transaction_type(self):
        return 'transfer'


class Referral(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    referrer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='referrer')
    referred_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='referred_user')
<<<<<<< HEAD
    date_created = models.DateTimeField(default=aware_datetime)
=======
    date_created = models.DateTimeField(default=now)
>>>>>>> e7942fca4e5bbb08501dbd878e781f7a78bf51a6
