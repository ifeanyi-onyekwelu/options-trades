from django.db import models
import uuid
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
import secrets
import string
import os
from django.conf import settings


def default_profile_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return os.path.join("profile images", filename)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_joined = models.DateTimeField(default=now)

    def __str__(self):
        return "{} {} - {}".format(self.first_name, self.last_name, self.email)

    def save(self, *args, **kwargs):
        random_username = self.get_random_username()
        if User.objects.filter(username=random_username).exists():
            random_username += "1"

        if not self.username:
            self.username = random_username

        super().save(*args, **kwargs)

    def get_random_username(self):
        alphabets = string.ascii_letters + string.digits
        random_username = "".join(secrets.choice(alphabets) for x in range(5))
        return random_username

    @property
    def get_type(self):
        return "user"


class UserBalance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Balance: ${self.balance}"


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10, unique=True)
    referred_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referred_by",
    )
    referral_link = models.URLField(null=True, blank=True)
    profile_img = models.ImageField(upload_to="profile images/", null=True, blank=True)
    address = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    zipcode = models.CharField(max_length=100, null=True)
    balance = models.OneToOneField(
        UserBalance, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.referral_code:
            referral_code = self.generate_referral_code()
            self.referral_code = referral_code

        if not self.referral_link:
            referral_link = self.generate_referral_link()
            self.referral_link = referral_link

        if not self.profile_img:
            self.profile_img = default_profile_image_path(
                self, "default_profile_image.png"
            )

        super().save(*args, **kwargs)

    def generate_referral_link(self):
        site_url = settings.APP_URL
        referral_link = f"{site_url}account/sign-up/?ref={self.referral_code}"
        return referral_link

    def generate_referral_code(self):
        alphabets = string.ascii_letters + string.digits
        referral_code = "".join(secrets.choice(alphabets) for x in range(6))
        return referral_code
