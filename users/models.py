from django.db import models
import uuid
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
import secrets
import string

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referral_code = models.CharField(max_length=10, unique=True)
    profile_img = models.ImageField(upload_to="profile images/", null=True, blank=True)
    address = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    bio = models.TextField(null=True, blank=True)
    wallet = models.OneToOneField(
        'UserWallet', on_delete=models.CASCADE, null=True, blank=True,related_name='user_wallet'
    )
    date_joined = models.DateTimeField(default=now)
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            alphabets = string.ascii_letters + string.digits
            referral_code = "".join(secrets.choice(alphabets) for x in range(6))
            self.referral_code = referral_code
        
        if not self.username and self.email:
            base_username = self.email.split('@')[0]
            self.username = base_username

            counter = 1
            while User.objects.filter(username=self.username).exists():
                self.username = f"{base_username}{counter}"
                counter += 1


        super().save(*args, **kwargs)

class UserWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
