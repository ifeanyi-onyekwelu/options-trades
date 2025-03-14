import uuid
import secrets
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referral_code = models.CharField(max_length=10, unique=True)
    profile_img = models.ImageField(upload_to="profile images/", null=True, blank=True)
    address = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            alphabets = string.ascii_letters + string.digits
            referral_code = "".join(secrets.choice(alphabets) for _ in range(6))
            self.referral_code = referral_code

        if not self.username and self.email:
            base_username = self.email.split("@")[0]
            self.username = base_username

            counter = 1
            while User.objects.filter(username=self.username).exists():
                self.username = f"{base_username}{counter}"
                counter += 1

        super().save(*args, **kwargs)


class UserWallet(models.Model):
    CRYPTO_CHOICES = [
        ("BTC", "Bitcoin"),
        ("USDT", "Tether"),
        ("ETH", "Ethereum"),
        ("LTC", "Litecoin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="wallets"
    )
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = models.CharField(
        max_length=10,
        choices=CRYPTO_CHOICES,
        default="BTC",  # Set a valid default currency
    )

    class Meta:
        unique_together = ("user", "currency")

    def __str__(self):
        return f"{self.currency} - {self.balance}"


@receiver(post_save, sender=get_user_model())
def create_user_wallets(sender, instance, created, **kwargs):
    if created and not instance.is_superuser and not instance.is_staff:
        currencies = ["BTC", "USDT", "ETH", "LTC"]
        for currency in currencies:
            UserWallet.objects.create(user=instance, currency=currency)
