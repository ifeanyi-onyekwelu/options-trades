# app/utils.py
from .models import Notification

def create_notification(user, title, description):
    Notification.objects.create(
        user=user,
        title=title,
        description=description
    )
