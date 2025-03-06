from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from users.models import UserWallet

@receiver(post_save, sender=get_user_model())
def create_user_balance(sender, instance, created, **kwargs):
    if created and not instance.is_superuser and not instance.is_staff:
        UserWallet.objects.create(user=instance)
