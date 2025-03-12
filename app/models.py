from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils.timezone import now
from django.utils.text import slugify
import os
from users.models import UserWallet


def default_profile_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return os.path.join("profile images", filename)


def calculate_returns(amount, investment_plan):
    daily_returns = (investment_plan.returns_percentage / 100) * amount
    total_returns = daily_returns * investment_plan.duration_days

    return round(total_returns, 2)


class InvestmentPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    maximum_price = models.DecimalField(max_digits=10, decimal_places=2)
    returns_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.IntegerField()
    total_returns_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    date_created = models.DateTimeField(default=now)

    def __str__(self):
        return "{}".format(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def get_type(self):
        return "investment_plan"


class UserInvestment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    investment_plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    returns = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(default=now)

    def __str__(self):
        return "Investment by {}. Plan - {}".format(self.user, self.investment_plan)

    def save(self, *args, **kwargs):
        returns = calculate_returns(self.amount, self.investment_plan)

        self.returns = returns

        super().save(*args, **kwargs)

    @property
    def get_type(self):
        return "user_investment"


class Deposit(models.Model):
    CRYPTO_CHOICES = (
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "Tether"),
        ("LTC", "Litecoin"),
    )
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    crypto_currency = models.CharField(
        max_length=10, choices=CRYPTO_CHOICES, blank=True, null=True
    )
    transaction_id = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="PENDING")
    date_created = models.DateTimeField(default=now)


class Withdraw(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_address = models.CharField(max_length=100, default="0")
    wallet = models.ForeignKey(
        UserWallet, on_delete=models.CASCADE, blank=True, null=True
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    date_created = models.DateTimeField(default=now)


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
